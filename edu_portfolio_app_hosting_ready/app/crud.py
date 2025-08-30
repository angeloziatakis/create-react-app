from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from . import models

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, email: str, password: str, role: models.RoleEnum):
    hashed_password = bcrypt.hash(password)
    user = models.User(email=email, hashed_password=hashed_password, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def verify_password(hashed_password: str, password: str) -> bool:
    return bcrypt.verify(password, hashed_password)

def create_assignment(db: Session, student_id: int, stored_filename: str, original_name: str):
    a = models.Assignment(student_id=student_id, filename=stored_filename, original_name=original_name)
    db.add(a); db.commit(); db.refresh(a)
    return a

def list_student_assignments(db: Session, student_id: int, q: str | None = None, status: str | None = None):
    query = db.query(models.Assignment).filter(models.Assignment.student_id == student_id)
    if q:
        query = query.filter(models.Assignment.original_name.ilike(f"%{q}%"))
    if status:
        query = query.filter(models.Assignment.status == status)
    return query.order_by(models.Assignment.uploaded_at.desc()).all()

def list_all_assignments(db: Session):
    return db.query(models.Assignment).order_by(models.Assignment.uploaded_at.desc()).all()

def save_ai_report(db: Session, assignment_id: int, report_json: str):
    a = db.query(models.Assignment).get(assignment_id)
    if a:
        a.ai_report = report_json
        db.commit()
        db.refresh(a)
    return a

def save_feedback(db: Session, assignment_id: int, feedback: str, status: models.AssignmentStatus):
    a = db.query(models.Assignment).get(assignment_id)
    if a:
        a.teacher_feedback = feedback
        a.status = status
        db.commit()
        db.refresh(a)
    return a

def create_material(db: Session, teacher_id: int, title: str, type_: models.MaterialType, path: str):
    m = models.Material(teacher_id=teacher_id, title=title, type=type_, path=path)
    db.add(m); db.commit(); db.refresh(m)
    return m

def list_materials(db: Session, teacher_id: int | None = None):
    q = db.query(models.Material)
    if teacher_id:
        q = q.filter(models.Material.teacher_id == teacher_id)
    return q.order_by(models.Material.uploaded_at.desc()).all()

def add_notification(db: Session, user_id: int, message: str):
    n = models.Notification(user_id=user_id, message=message)
    db.add(n); db.commit(); db.refresh(n)
    return n

def list_notifications(db: Session, user_id: int):
    return db.query(models.Notification).filter(models.Notification.user_id == user_id).order_by(models.Notification.created_at.desc()).all()

def mark_notifications_read(db: Session, user_id: int):
    db.query(models.Notification).filter(models.Notification.user_id == user_id).update({models.Notification.is_read: True})
    db.commit()
