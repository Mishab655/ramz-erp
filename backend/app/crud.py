from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas
from .core.security import get_password_hash

# User
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, password_hash=hashed_password, full_name=user.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Branch
def get_branches(db: Session, skip: int = 0, limit: int = 100):
    branches = db.query(models.Branch).offset(skip).limit(limit).all()
    # attach employee count
    for branch in branches:
        branch.employee_count = db.query(models.Employee).filter(models.Employee.branch_id == branch.id).count()
    return branches

def create_branch(db: Session, branch: schemas.BranchCreate):
    db_branch = models.Branch(name=branch.name)
    db.add(db_branch)
    db.commit()
    db.refresh(db_branch)
    return db_branch

def get_branch(db: Session, branch_id: int):
    return db.query(models.Branch).filter(models.Branch.id == branch_id).first()

def update_branch(db: Session, branch_id: int, branch: schemas.BranchUpdate):
    db_branch = db.query(models.Branch).filter(models.Branch.id == branch_id).first()
    if not db_branch:
        return None
    db_branch.name = branch.name
    db.commit()
    db.refresh(db_branch)
    return db_branch

def delete_branch(db: Session, branch_id: int):
    db_branch = db.query(models.Branch).filter(models.Branch.id == branch_id).first()
    if db_branch:
        db.delete(db_branch)
        db.commit()
        return True
    return False

# Employee
def get_employees(db: Session, skip: int = 0, limit: int = 100, branch_id: int = None, search: str = None):
    query = db.query(models.Employee).filter(models.Employee.is_deleted == False)
    if branch_id:
        query = query.filter(models.Employee.branch_id == branch_id)
    if search:
        query = query.filter(models.Employee.full_name.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()

def get_trashed_employees(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Employee).filter(models.Employee.is_deleted == True).offset(skip).limit(limit).all()

def get_employee(db: Session, employee_id: int):
    return db.query(models.Employee).filter(models.Employee.id == employee_id).first()

def create_employee(db: Session, employee: schemas.EmployeeCreate):
    db_emp = models.Employee(**employee.dict())
    db.add(db_emp)
    db.commit()
    db.refresh(db_emp)
    return db_emp

def update_employee(db: Session, employee_id: int, employee: schemas.EmployeeUpdate):
    db_emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not db_emp:
        return None
    update_data = employee.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_emp, key, value)
    db.commit()
    db.refresh(db_emp)
    return db_emp

def delete_employee(db: Session, employee_id: int):
    from datetime import datetime
    db_emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if db_emp:
        db_emp.is_deleted = True
        db_emp.deleted_at = datetime.utcnow()
        db.commit()
        return True
    return False

def restore_employee(db: Session, employee_id: int):
    db_emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if db_emp:
        db_emp.is_deleted = False
        db_emp.deleted_at = None
        db.commit()
        return True
    return False

# Dashboard Stats
def get_dashboard_stats(db: Session):
    total_employees = db.query(models.Employee).filter(models.Employee.is_deleted == False).count()
    total_branches = db.query(models.Branch).count()
    
    from datetime import datetime, timedelta
    sixty_days_from_now = datetime.now() + timedelta(days=60)
    
    # Get count of documents expiring within 60 days
    documents_expiring_soon = db.query(models.Document).filter(models.Document.expiry_date <= sixty_days_from_now).count()
    
    total_salary_pending = db.query(func.sum(models.Employee.salary_pending)).filter(models.Employee.is_deleted == False).scalar() or 0.0
    
    recent_employees = db.query(models.Employee).filter(models.Employee.is_deleted == False).order_by(models.Employee.created_at.desc()).limit(5).all()

    return {
        "total_employees": total_employees,
        "total_branches": total_branches,
        "documents_expiring_soon": documents_expiring_soon,
        "total_salary_pending": total_salary_pending,
        "recent_employees": recent_employees
    }
