from fastapi import APIRouter, status
from app.api.dependencies import CurrentUser, DatabaseSession
from app.schemas.common import APIResponse
from app.schemas.operations import *
from app.services.operations_service import OperationsService
router=APIRouter(prefix="/lifecycle-profiles/{profile_id}/operations")
@router.get("",response_model=APIResponse[OperationsSnapshot])
def get_ops(profile_id:str,user:CurrentUser,session:DatabaseSession):
 e,t,a,attendance,leave_requests=OperationsService(session).snapshot(user,profile_id);return APIResponse(data=OperationsSnapshot(employees=[EmployeeResponse.model_validate(x) for x in e],tasks=[TaskResponse.model_validate(x) for x in t],announcements=[AnnouncementResponse.model_validate(x) for x in a],attendance=[AttendanceResponse.model_validate(x) for x in attendance],leave_requests=[LeaveRequestResponse.model_validate(x) for x in leave_requests]))
@router.post("/employees",response_model=APIResponse[EmployeeResponse],status_code=status.HTTP_201_CREATED)
def employee(profile_id:str,payload:EmployeeCreate,user:CurrentUser,session:DatabaseSession): return APIResponse(data=EmployeeResponse.model_validate(OperationsService(session).add_employee(user,profile_id,payload.full_name,payload.job_title)))
@router.post("/tasks",response_model=APIResponse[TaskResponse],status_code=status.HTTP_201_CREATED)
def task(profile_id:str,payload:TaskCreate,user:CurrentUser,session:DatabaseSession): return APIResponse(data=TaskResponse.model_validate(OperationsService(session).add_task(user,profile_id,payload.title,payload.assigned_employee_id)))
@router.patch("/tasks/{task_id}",response_model=APIResponse[TaskResponse])
def task_status(profile_id:str,task_id:str,payload:TaskStatusUpdate,user:CurrentUser,session:DatabaseSession): return APIResponse(data=TaskResponse.model_validate(OperationsService(session).set_task(user,profile_id,task_id,payload.status)))
@router.post("/announcements",response_model=APIResponse[AnnouncementResponse],status_code=status.HTTP_201_CREATED)
def announcement(profile_id:str,payload:AnnouncementCreate,user:CurrentUser,session:DatabaseSession): return APIResponse(data=AnnouncementResponse.model_validate(OperationsService(session).add_announcement(user,profile_id,payload.message)))
@router.put("/attendance",response_model=APIResponse[AttendanceResponse])
def attendance(profile_id:str,payload:AttendanceUpsert,user:CurrentUser,session:DatabaseSession): return APIResponse(data=AttendanceResponse.model_validate(OperationsService(session).record_attendance(user,profile_id,payload.employee_id,payload.attendance_date,payload.status)))
@router.post("/leave-requests",response_model=APIResponse[LeaveRequestResponse],status_code=status.HTTP_201_CREATED)
def leave_request(profile_id:str,payload:LeaveRequestCreate,user:CurrentUser,session:DatabaseSession): return APIResponse(data=LeaveRequestResponse.model_validate(OperationsService(session).request_leave(user,profile_id,payload.employee_id,payload.start_date,payload.end_date,payload.reason)))
