"""Profile-owned business operations records."""

from datetime import date

from sqlalchemy import Date, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Employee(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "employees"
    startup_profile_id: Mapped[str] = mapped_column(ForeignKey("startup_profiles.id", ondelete="CASCADE"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    job_title: Mapped[str | None] = mapped_column(String(120), nullable=True)
    employment_status: Mapped[str] = mapped_column(String(24), nullable=False, default="active")
    __table_args__ = (Index("ix_employees_profile_status", "startup_profile_id", "employment_status"),)


class AttendanceRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "attendance_records"
    employee_id: Mapped[str] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    attendance_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    __table_args__ = (Index("uq_attendance_employee_date", "employee_id", "attendance_date", unique=True),)


class LeaveRequest(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "leave_requests"
    employee_id: Mapped[str] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="pending")


class OperationTask(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "operation_tasks"
    startup_profile_id: Mapped[str] = mapped_column(ForeignKey("startup_profiles.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    assigned_employee_id: Mapped[str | None] = mapped_column(ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="todo")
    __table_args__ = (Index("ix_operation_tasks_profile_status", "startup_profile_id", "status"),)


class Announcement(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "announcements"
    startup_profile_id: Mapped[str] = mapped_column(ForeignKey("startup_profiles.id", ondelete="CASCADE"), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
