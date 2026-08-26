"""Owner-scoped persistence for business operations."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.models.lifecycle import StartupProfile
from app.models.operations import Announcement, AttendanceRecord, Employee, LeaveRequest, OperationTask
from app.models.user import User


class OperationsService:
    def __init__(self, session: Session):
        self.session = session

    def _profile(self, user: User, profile_id: str) -> StartupProfile:
        profile = self.session.get(StartupProfile, profile_id)
        if not profile or profile.created_by_id != user.id:
            raise ResourceNotFoundError("Startup profile was not found.")
        return profile

    def _employee(self, user: User, profile_id: str, employee_id: str) -> Employee:
        self._profile(user, profile_id)
        employee = self.session.get(Employee, employee_id)
        if not employee or employee.startup_profile_id != profile_id:
            raise ResourceNotFoundError("Employee was not found.")
        return employee

    def snapshot(self, user: User, profile_id: str):
        self._profile(user, profile_id)
        employees = list(self.session.scalars(select(Employee).where(Employee.startup_profile_id == profile_id)))
        employee_ids = [employee.id for employee in employees]
        attendance = [] if not employee_ids else list(self.session.scalars(
            select(AttendanceRecord).where(AttendanceRecord.employee_id.in_(employee_ids))
        ))
        leave_requests = [] if not employee_ids else list(self.session.scalars(
            select(LeaveRequest).where(LeaveRequest.employee_id.in_(employee_ids)).order_by(LeaveRequest.created_at.desc())
        ))
        tasks = list(self.session.scalars(select(OperationTask).where(OperationTask.startup_profile_id == profile_id)))
        announcements = list(self.session.scalars(
            select(Announcement).where(Announcement.startup_profile_id == profile_id).order_by(Announcement.created_at.desc())
        ))
        return employees, tasks, announcements, attendance, leave_requests

    def add_employee(self, user: User, profile_id: str, name: str, title: str | None) -> Employee:
        self._profile(user, profile_id)
        employee = Employee(startup_profile_id=profile_id, full_name=name, job_title=title)
        self.session.add(employee)
        self.session.commit()
        self.session.refresh(employee)
        return employee

    def add_task(self, user: User, profile_id: str, title: str, assignee: str | None) -> OperationTask:
        self._profile(user, profile_id)
        if assignee:
            self._employee(user, profile_id, assignee)
        task = OperationTask(startup_profile_id=profile_id, title=title, assigned_employee_id=assignee)
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def set_task(self, user: User, profile_id: str, task_id: str, status: str) -> OperationTask:
        self._profile(user, profile_id)
        task = self.session.get(OperationTask, task_id)
        if not task or task.startup_profile_id != profile_id:
            raise ResourceNotFoundError("Task was not found.")
        task.status = status
        self.session.commit()
        self.session.refresh(task)
        return task

    def add_announcement(self, user: User, profile_id: str, message: str) -> Announcement:
        self._profile(user, profile_id)
        announcement = Announcement(startup_profile_id=profile_id, message=message)
        self.session.add(announcement)
        self.session.commit()
        self.session.refresh(announcement)
        return announcement

    def record_attendance(self, user: User, profile_id: str, employee_id: str, attendance_date: date, status: str) -> AttendanceRecord:
        self._employee(user, profile_id, employee_id)
        record = self.session.scalar(select(AttendanceRecord).where(
            AttendanceRecord.employee_id == employee_id,
            AttendanceRecord.attendance_date == attendance_date,
        ))
        if record:
            record.status = status
        else:
            record = AttendanceRecord(employee_id=employee_id, attendance_date=attendance_date, status=status)
            self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def request_leave(self, user: User, profile_id: str, employee_id: str, start_date: date, end_date: date, reason: str | None) -> LeaveRequest:
        self._employee(user, profile_id, employee_id)
        if end_date < start_date:
            raise ValueError("Leave end date cannot be before the start date.")
        request = LeaveRequest(employee_id=employee_id, start_date=start_date, end_date=end_date, reason=reason)
        self.session.add(request)
        self.session.commit()
        self.session.refresh(request)
        return request
