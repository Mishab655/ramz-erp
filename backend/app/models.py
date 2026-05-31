from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base

class StatusEnum(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    full_name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    employees = relationship("Employee", back_populates="branch")

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"))
    full_name = Column(String, index=True)
    place = Column(String)
    address = Column(String)
    phone_number = Column(String)
    photo_url = Column(String, nullable=True)
    emirates_id = Column(String)
    emirates_id_expiry = Column(DateTime(timezone=True))
    visa_date = Column(DateTime(timezone=True))
    visa_expiry = Column(DateTime(timezone=True))
    passport_number = Column(String)
    joined_date = Column(DateTime(timezone=True))
    salary = Column(Float)
    salary_pending = Column(Float, default=0.0)
    status = Column(Enum(StatusEnum), default=StatusEnum.ACTIVE)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    branch = relationship("Branch", back_populates="employees")
    remarks = relationship("Remark", back_populates="employee")
    documents = relationship("Document", back_populates="employee")

class Remark(Base):
    __tablename__ = "remarks"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    note = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee", back_populates="remarks")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    title = Column(String)
    file_url = Column(String, nullable=True)
    file_url_2 = Column(String, nullable=True)
    document_type = Column(String) # e.g. Passport, Visa, ID, Other
    issue_date = Column(DateTime(timezone=True), nullable=True)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee", back_populates="documents")
