# Educational Portfolio App (Phase 1) — FastAPI

A minimal, working scaffold of the Educational Portfolio App described in the spec.  
Built with **FastAPI**, **SQLAlchemy**, **Jinja2**, and **SQLite**. Uses cookie-based sessions for simple role-based auth.

## Features in this scaffold
- Teacher & Student roles with login/register.
- Role-based dashboards.
- Individual student portfolio view.
- Assignment upload (PDF, images, video, etc.) with storage on disk.
- AI pre-check **stub** that creates a simple report (sent to teacher dashboard only).
- Teacher correction workflow: add comments/feedback & status.
- Educational materials upload (teacher).
- Notifications when students upload new assignments (visible to teachers).
- Parent report generation (PDF) with very basic charts text (placeholder).
- Search & filter in assignment history (by status or filename substring).
- Basic security: password hashing, session-based auth, role-based access checks.

> This is a starter kit, not production-ready. Improve security, validation, file scanning, access controls, logging, rate limiting, and error handling before production use.

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Then open: http://127.0.0.1:8000

## Default Flow
1. Register a **Teacher** and a **Student** (temporary convenience route `/register`).
2. Login as Student → upload an assignment at **Student Dashboard**.
3. Login as Teacher → see **Notifications** and **AI Reports**; open an assignment and add feedback.
4. Generate a PDF report for a student from the Teacher area.

## Notes
- Files saved under `app/uploads/` and `app/materials/`.
- AI pre-check is a simple heuristic (counts long words, non-letters, naive spell-ish ratio on .txt files). Replace with a real model later.
- Report generation uses `reportlab` for a simple PDF placeholder.

## Structure
```
app/
  main.py             # FastAPI app, routes, session middleware
  database.py         # SQLAlchemy engine/session
  models.py           # ORM models
  crud.py             # DB helpers
  deps.py             # shared dependencies (auth/session/db)
  auth.py             # login/logout/register
  ai_precheck.py      # stub analyzer
  notifications.py    # simple notifications
  reports.py          # PDF generation
  schemas.py          # pydantic schemas (lightly used)
  templates/          # Jinja HTML templates
  static/             # static assets
  uploads/            # uploaded assignments
  materials/          # uploaded materials
```
