"""Operations API contracts."""
from datetime import date
from pydantic import BaseModel, ConfigDict, Field

class EmployeeCreate(BaseModel): full_name: str = Field(min_length=2, max_length=160); job_title: str | None = Field(default=None, max_length=120)
class EmployeeResponse(EmployeeCreate): model_config = ConfigDict(from_attributes=True); id: str; employment_status: str
class AttendanceUpsert(BaseModel): employee_id: str; attendance_date: date; status: str = Field(pattern="^(present|absent|leave)$")
class AttendanceResponse(AttendanceUpsert): model_config = ConfigDict(from_attributes=True); id: str
class LeaveRequestCreate(BaseModel):
    employee_id: str
    start_date: date
    end_date: date
    reason: str | None = Field(default=None, max_length=5_000)
class LeaveRequestResponse(LeaveRequestCreate): model_config = ConfigDict(from_attributes=True); id: str; status: str
class TaskCreate(BaseModel): title: str = Field(min_length=2, max_length=240); assigned_employee_id: str | None = None
class TaskResponse(TaskCreate): model_config = ConfigDict(from_attributes=True); id: str; status: str
class TaskStatusUpdate(BaseModel): status: str = Field(pattern="^(todo|done)$")
class AnnouncementCreate(BaseModel): message: str = Field(min_length=2, max_length=5000)
class AnnouncementResponse(AnnouncementCreate): model_config = ConfigDict(from_attributes=True); id: str
class OperationsSnapshot(BaseModel):
    employees: list[EmployeeResponse]
    tasks: list[TaskResponse]
    announcements: list[AnnouncementResponse]
    attendance: list[AttendanceResponse]
    leave_requests: list[LeaveRequestResponse]
