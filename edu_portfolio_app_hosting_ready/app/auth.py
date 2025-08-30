from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from .database import get_db
from . import crud, models

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return request.app.state.templates.TemplateResponse("login.html", {"request": request, "error": None})

@router.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email)
    if not user or not crud.verify_password(user.hashed_password, password):
        return request.app.state.templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    request.session["user"] = {"id": user.id, "email": user.email, "role": user.role.value}
    if user.role == models.RoleEnum.teacher:
        return RedirectResponse(url="/teacher/dashboard", status_code=303)
    else:
        return RedirectResponse(url="/student/dashboard", status_code=303)

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

# Temporary registration route for demo
@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return request.app.state.templates.TemplateResponse("register.html", {"request": request, "error": None})

@router.post("/register")
def register(request: Request, email: str = Form(...), password: str = Form(...), role: str = Form(...), db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, email):
        return request.app.state.templates.TemplateResponse("register.html", {"request": request, "error": "Email already registered"})
    role_enum = models.RoleEnum(role)
    user = crud.create_user(db, email, password, role_enum)
    request.session["user"] = {"id": user.id, "email": user.email, "role": user.role.value}
    if role_enum == models.RoleEnum.teacher:
        return RedirectResponse(url="/teacher/dashboard", status_code=303)
    return RedirectResponse(url="/student/dashboard", status_code=303)
