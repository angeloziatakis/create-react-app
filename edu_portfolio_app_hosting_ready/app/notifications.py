from sqlalchemy.orm import Session
from . import crud

def notify_teacher_of_upload(db: Session, teacher_ids: list[int], student_email: str, assignment_name: str):
    for tid in teacher_ids:
        crud.add_notification(db, tid, f"New assignment from {student_email}: {assignment_name}")
