import { apiClient } from '@/api/client'
import type { APIResponse } from '@/types/api'

export interface Employee { id: string; full_name: string; job_title: string | null; employment_status: string }
export interface OperationTask { id: string; title: string; assigned_employee_id: string | null; status: 'todo' | 'done' }
export interface Announcement { id: string; message: string }
export interface AttendanceRecord { id: string; employee_id: string; attendance_date: string; status: 'present' | 'absent' | 'leave' }
export interface LeaveRequest { id: string; employee_id: string; start_date: string; end_date: string; reason: string | null; status: string }
export interface OperationsSnapshot { employees: Employee[]; tasks: OperationTask[]; announcements: Announcement[]; attendance: AttendanceRecord[]; leave_requests: LeaveRequest[] }

const base = (profileId: string) => `/lifecycle-profiles/${profileId}/operations`

export const operationsApi = {
  getSnapshot: async (profileId: string) => (await apiClient.get<APIResponse<OperationsSnapshot>>(base(profileId))).data.data,
  addEmployee: async (profileId: string, payload: { full_name: string; job_title?: string | null }) => (await apiClient.post<APIResponse<Employee>>(`${base(profileId)}/employees`, payload)).data.data,
  addTask: async (profileId: string, payload: { title: string; assigned_employee_id?: string | null }) => (await apiClient.post<APIResponse<OperationTask>>(`${base(profileId)}/tasks`, payload)).data.data,
  updateTask: async (profileId: string, taskId: string, status: 'todo' | 'done') => (await apiClient.patch<APIResponse<OperationTask>>(`${base(profileId)}/tasks/${taskId}`, { status })).data.data,
  addAnnouncement: async (profileId: string, message: string) => (await apiClient.post<APIResponse<Announcement>>(`${base(profileId)}/announcements`, { message })).data.data,
  recordAttendance: async (profileId: string, employeeId: string, status: 'present' | 'absent' | 'leave') => (await apiClient.put<APIResponse<AttendanceRecord>>(`${base(profileId)}/attendance`, { employee_id: employeeId, attendance_date: new Date().toISOString().slice(0, 10), status })).data.data,
  requestLeave: async (profileId: string, payload: { employee_id: string; start_date: string; end_date: string; reason?: string | null }) => (await apiClient.post<APIResponse<LeaveRequest>>(`${base(profileId)}/leave-requests`, payload)).data.data,
}
