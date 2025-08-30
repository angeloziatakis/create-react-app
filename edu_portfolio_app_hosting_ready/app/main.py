import os, json
from datetime import datetime
from fastapi import FastAPI, Request, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from . import models, crud
from .deps import require_role, require_login
from .ai_precheck import analyze_file
from .notifications import notify_teacher_of_upload
from .reports import build_student_report

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Educational Portfolio App - Phase 1")

# Jinja2
templates_env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
    autoescape=select_autoescape(["html", "xml"]),
)
app.state.templates = templates_env

# Static & uploads
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

# Sessions
app.add_middleware(SessionMiddleware, secret_key=os.environ.get("SESSION_SECRET", "dev-secret-change-me"), same_site="lax")

# Routers
from .auth import router as auth_router
app.include_router(auth_router)

def render(request: Request, template: str, ctx: dict):
    return app.state.templates.get_template(template).render(ctx | {"request": request})

# Index -> redirect
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return RedirectResponse(url=f"/{user['role']}/dashboard", status_code=303)

# ---------------- Student Area ----------------
@app.get("/student/dashboard", response_class=HTMLResponse)
@require_role("student")
async def student_dashboard(request: Request, db: Session = Depends(get_db), q: str | None = None, status: str | None = None):
    user = request.session["user"]
    assignments = crud.list_student_assignments(db, user["id"], q=q, status=status)
    html = render(request, "student_dashboard.html", {"user": user, "assignments": assignments, "q": q or "", "status": status or ""})
    return HTMLResponse(html)

@app.get("/student/upload", response_class=HTMLResponse)
@require_role("student")
async def student_upload_page(request: Request):
    html = render(request, "upload_assignment.html", {"user": request.session["user"], "error": None})
    return HTMLResponse(html)

@app.post("/student/upload")
@require_role("student")
async def student_upload(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    user = request.session["user"]
    uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    stored_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    path = os.path.join(uploads_dir, stored_name)
    with open(path, "wb") as f:
        f.write(await file.read())

    assignment = crud.create_assignment(db, student_id=user["id"], stored_filename=stored_name, original_name=file.filename)

    # AI pre-check (teacher only)
    report = analyze_file(path)
    crud.save_ai_report(db, assignment.id, json.dumps(report))

    # Notify all teachers (simple broadcast to all teacher users)
    teachers = db.query(models.User).filter(models.User.role == models.RoleEnum.teacher).all()
    notify_teacher_of_upload(db, [t.id for t in teachers], user["email"], file.filename)

    return RedirectResponse(url="/student/dashboard", status_code=303)

# ---------------- Teacher Area ----------------
@app.get("/teacher/dashboard", response_class=HTMLResponse)
@require_role("teacher")
async def teacher_dashboard(request: Request, db: Session = Depends(get_db)):
    user = request.session["user"]
    assignments = crud.list_all_assignments(db)
    materials = crud.list_materials(db, teacher_id=user["id"])
    notifications = crud.list_notifications(db, user_id=user["id"])
    html = render(request, "teacher_dashboard.html", {"user": user, "assignments": assignments, "materials": materials, "notifications": notifications})
    return HTMLResponse(html)

@app.get("/teacher/assignment/{assignment_id}", response_class=HTMLResponse)
@require_role("teacher")
async def teacher_view_assignment(request: Request, assignment_id: int, db: Session = Depends(get_db)):
    a = db.query(models.Assignment).get(assignment_id)
    if not a:
        raise HTTPException(status_code=404, detail="Assignment not found")
    ai_report = json.loads(a.ai_report) if a.ai_report else None
    html = render(request, "view_assignment.html", {"user": request.session["user"], "a": a, "ai_report": ai_report})
    return HTMLResponse(html)

@app.post("/teacher/assignment/{assignment_id}/feedback")
@require_role("teacher")
async def teacher_feedback(request: Request, assignment_id: int, feedback: str = Form(""), status: str = Form("reviewed"), db: Session = Depends(get_db)):
    status_enum = models.AssignmentStatus(status)
    crud.save_feedback(db, assignment_id, feedback, status_enum)
    return RedirectResponse(url=f"/teacher/assignment/{assignment_id}", status_code=303)

@app.get("/uploads/{filename}")
@require_login
async def get_upload(filename: str):
    path = os.path.join(os.path.dirname(__file__), "uploads", filename)
    return FileResponse(path)

# Materials
@app.post("/teacher/materials/upload")
@require_role("teacher")
async def upload_material(request: Request, title: str = Form(...), type: str = Form("document"), file: UploadFile = File(...), db: Session = Depends(get_db)):
    user = request.session["user"]
    mat_dir = os.path.join(os.path.dirname(__file__), "materials")
    os.makedirs(mat_dir, exist_ok=True)
    stored_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    path = os.path.join(mat_dir, stored_name)
    with open(path, "wb") as f:
        f.write(await file.read())
    crud.create_material(db, teacher_id=user["id"], title=title, type_=models.MaterialType(type), path=stored_name)
    return RedirectResponse(url="/teacher/dashboard", status_code=303)

@app.get("/materials/{filename}")
@require_login
async def get_material(filename: str):
    path = os.path.join(os.path.dirname(__file__), "materials", filename)
    return FileResponse(path)

# Parent report (PDF)
@app.get("/teacher/report/{student_id}")
@require_role("teacher")
async def student_report(request: Request, student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.User).get(student_id)
    if not student or student.role != models.RoleEnum.student:
        raise HTTPException(status_code=404, detail="Student not found")
    assignments = crud.list_student_assignments(db, student_id=student_id)
    status_counts = {"total": len(assignments), "submitted": 0, "reviewed": 0, "returned": 0}
    for a in assignments:
        status_counts[a.status.value] += 1
    pdf_bytes = build_student_report(student.email, assignments, status_counts)
    fname = f"report_{student_id}.pdf"
    fpath = os.path.join(os.path.dirname(__file__), fname)
    with open(fpath, "wb") as f:
        f.write(pdf_bytes)
    return FileResponse(fpath, media_type="application/pdf", filename=fname)

# ---------------- Templates rendering helpers ----------------
from fastapi import APIRouter
pages = APIRouter()

@app.get("/portfolio", response_class=HTMLResponse)
@require_role("student")
async def portfolio_page(request: Request, db: Session = Depends(get_db)):
    user = request.session["user"]
    assignments = crud.list_student_assignments(db, user["id"])
    html = render(request, "portfolio.html", {"user": user, "assignments": assignments})
    return HTMLResponse(html)
