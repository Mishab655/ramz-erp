from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from .models import StatusEnum

# Users
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    created_at: datetime

    class Config:
        from_attributes = True

# Branches
class BranchBase(BaseModel):
    name: str

class BranchCreate(BranchBase):
    pass

class BranchUpdate(BranchBase):
    pass

class BranchResponse(BranchBase):
    id: int
    created_at: datetime
    employee_count: Optional[int] = 0

    class Config:
        from_attributes = True

# Remarks
class RemarkCreate(BaseModel):
    note: str

class RemarkResponse(BaseModel):
    id: int
    note: str
    created_at: datetime
    user_id: int
    employee_id: int

    class Config:
        from_attributes = True

# Documents
class DocumentResponse(BaseModel):
    id: int
    title: str
    file_url: Optional[str] = None
    file_url_2: Optional[str] = None
    document_type: str
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    uploaded_at: datetime
    employee_id: int

    class Config:
        from_attributes = True

# Employees
class EmployeeBase(BaseModel):
    full_name: str
    place: str
    address: str
    phone_number: str
    emirates_id: str
    emirates_id_expiry: datetime
    visa_date: datetime
    visa_expiry: datetime
    passport_number: str
    joined_date: datetime
    salary: float
    salary_pending: float = 0.0
    status: StatusEnum = StatusEnum.ACTIVE

class EmployeeCreate(EmployeeBase):
    branch_id: int
    photo_url: Optional[str] = None

class EmployeeUpdate(BaseModel):
    branch_id: Optional[int] = None
    full_name: Optional[str] = None
    place: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    emirates_id: Optional[str] = None
    emirates_id_expiry: Optional[datetime] = None
    visa_date: Optional[datetime] = None
    visa_expiry: Optional[datetime] = None
    passport_number: Optional[str] = None
    joined_date: Optional[datetime] = None
    salary: Optional[float] = None
    salary_pending: Optional[float] = None
    status: Optional[StatusEnum] = None
    photo_url: Optional[str] = None

class EmployeeResponse(EmployeeBase):
    id: int
    branch_id: int
    photo_url: Optional[str] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class EmployeeDetailResponse(EmployeeResponse):
    branch: BranchResponse
    remarks: List[RemarkResponse] = []
    documents: List[DocumentResponse] = []

    class Config:
        from_attributes = True

# Token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
