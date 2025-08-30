from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from .database import Base
import enum

class RoleEnum(str, enum.Enum):
    teacher = "teacher"
    student = "student"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    assignments = relationship("Assignment", back_populates="student", foreign_keys="Assignment.student_id")
    materials = relationship("Material", back_populates="teacher", foreign_keys="Material.teacher_id")

class AssignmentStatus(str, enum.Enum):
    submitted = "submitted"
    reviewed = "reviewed"
    returned = "returned"

class Assignment(Base):
    __tablename__ = "assignments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    filename: Mapped[str] = mapped_column(String, nullable=False)
    original_name: Mapped[str] = mapped_column(String, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ai_report: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string; visible to teacher
    teacher_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[AssignmentStatus] = mapped_column(Enum(AssignmentStatus), default=AssignmentStatus.submitted)

    student = relationship("User", back_populates="assignments", foreign_keys=[student_id])

class MaterialType(str, enum.Enum):
    video = "video"
    game = "game"
    quiz = "quiz"
    document = "document"

class Material(Base):
    __tablename__ = "materials"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[MaterialType] = mapped_column(Enum(MaterialType), default=MaterialType.document)
    path: Mapped[str] = mapped_column(String, nullable=False)  # file path or URL
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    teacher = relationship("User", back_populates="materials", foreign_keys=[teacher_id])

class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    message: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
