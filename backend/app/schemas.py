from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from .models import AllocationStatus, EmployeeStatus, ProjectStatus, SeatStatus

class ProjectCreate(BaseModel): name: str; description: str | None = None; manager_name: str | None = None; status: ProjectStatus = ProjectStatus.ACTIVE
class ProjectOut(ProjectCreate): id: int; created_at: datetime; model_config = ConfigDict(from_attributes=True)
class EmployeeCreate(BaseModel):
    employee_code: str | None = None; name: str = Field(min_length=2); email: EmailStr; department: str; role: str; joining_date: date; project_id: int; status: EmployeeStatus = EmployeeStatus.ACTIVE
class EmployeeUpdate(BaseModel):
    name: str | None = None; email: EmailStr | None = None; department: str | None = None; role: str | None = None; joining_date: date | None = None; project_id: int | None = None; status: EmployeeStatus | None = None
class AllocationOut(BaseModel): id: int; seat_id: int; allocation_status: AllocationStatus; allocation_date: datetime; released_date: datetime | None; model_config = ConfigDict(from_attributes=True)
class EmployeeOut(BaseModel):
    id: int; employee_code: str; name: str; email: EmailStr; department: str; role: str; joining_date: date; status: EmployeeStatus; project_id: int; created_at: datetime; updated_at: datetime; project: ProjectOut | None = None; model_config = ConfigDict(from_attributes=True)
class SeatCreate(BaseModel): floor: int = Field(ge=1); zone: str; bay: str; seat_number: str; status: SeatStatus = SeatStatus.AVAILABLE
class SeatUpdate(BaseModel): status: SeatStatus
class SeatOut(SeatCreate): id: int; created_at: datetime; model_config = ConfigDict(from_attributes=True)
class AllocateRequest(BaseModel): employee_id: int; seat_id: int
class ReleaseRequest(BaseModel): employee_id: int | None = None; seat_id: int | None = None
class AssistantQuery(BaseModel): query: str = Field(min_length=2)
class AssistantAnswer(BaseModel): answer: str
