from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import shutil
from supabase import create_client, Client
from .. import crud, schemas, database, models

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_file_handler(file_obj, filename: str) -> str:
    if supabase:
        try:
            file_bytes = file_obj.read()
            # Use upsert to overwrite if file already exists
            supabase.storage.from_("ramz-uploads").upload(filename, file_bytes, file_options={"upsert": "true"})
            res = supabase.storage.from_("ramz-uploads").get_public_url(filename)
            return res
        except Exception as e:
            print(f"Supabase upload error: {e}")
            # Fallback to local if Supabase fails (e.g. bucket doesn't exist)
            pass
    
    # Fallback to local storage
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file_obj, buffer)
        return f"/uploads/{filename}"
from .auth import get_current_user

router = APIRouter(prefix="/employees", tags=["Employees"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas.EmployeeResponse])
def read_employees(skip: int = 0, limit: int = 100, branch_id: Optional[int] = None, search: Optional[str] = None, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    employees = crud.get_employees(db, skip=skip, limit=limit, branch_id=branch_id, search=search)
    return employees

@router.get("/trashed", response_model=List[schemas.EmployeeResponse])
def read_trashed_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    employees = crud.get_trashed_employees(db, skip=skip, limit=limit)
    return employees

@router.get("/{employee_id}", response_model=schemas.EmployeeDetailResponse)
def read_employee(employee_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_emp = crud.get_employee(db, employee_id=employee_id)
    if db_emp is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_emp

@router.post("/", response_model=schemas.EmployeeResponse)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_employee(db=db, employee=employee)

@router.put("/{employee_id}", response_model=schemas.EmployeeResponse)
def update_employee(employee_id: int, employee: schemas.EmployeeUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_emp = crud.update_employee(db=db, employee_id=employee_id, employee=employee)
    if not db_emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_emp

@router.delete("/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    success = crud.delete_employee(db, employee_id)
    if not success:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}

@router.post("/{employee_id}/restore")
def restore_employee(employee_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    success = crud.restore_employee(db, employee_id)
    if not success:
        raise HTTPException(status_code=404, detail="Employee not found or not trashed")
    return {"message": "Employee restored successfully"}

# Upload routes for documents & photos
UPLOAD_DIR = "backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/{employee_id}/upload_photo")
def upload_employee_photo(employee_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_emp = crud.get_employee(db, employee_id=employee_id)
    if not db_emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    filename = f"photo_{employee_id}_{file.filename}"
    file_url = upload_file_handler(file.file, filename)
    
    # Update employee record
    db_emp.photo_url = file_url
    db.commit()
    return {"photo_url": db_emp.photo_url}

@router.post("/{employee_id}/upload_document")
def upload_employee_document(employee_id: int, document_type: str = Form(...), title: str = Form(...), issue_date: Optional[str] = Form(None), expiry_date: Optional[str] = Form(None), file1: Optional[UploadFile] = File(None), file2: Optional[UploadFile] = File(None), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_emp = crud.get_employee(db, employee_id=employee_id)
    if not db_emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    file_url_1 = None
    file_url_2 = None

    if file1 and file1.filename:
        filename_1 = f"doc_{employee_id}_1_{file1.filename}"
        file_url_1 = upload_file_handler(file1.file, filename_1)
        
    if file2 and file2.filename:
        filename_2 = f"doc_{employee_id}_2_{file2.filename}"
        file_url_2 = upload_file_handler(file2.file, filename_2)
    
    i_date = None
    e_date = None
    if issue_date:
        try:
            i_date = datetime.strptime(issue_date, "%Y-%m-%d")
        except ValueError:
            pass
    if expiry_date:
        try:
            e_date = datetime.strptime(expiry_date, "%Y-%m-%d")
        except ValueError:
            pass

    core_types = ["Passport", "Visa", "Emirates ID", "Insurance", "Labour Card"]
    
    if document_type in core_types:
        # Upsert logic
        existing_doc = db.query(models.Document).filter(
            models.Document.employee_id == employee_id,
            models.Document.document_type == document_type
        ).first()
        
        if existing_doc:
            if file_url_1:
                existing_doc.file_url = file_url_1
            if file_url_2:
                existing_doc.file_url_2 = file_url_2
            if i_date or issue_date == "":
                existing_doc.issue_date = i_date
            if e_date or expiry_date == "":
                existing_doc.expiry_date = e_date
            existing_doc.title = title
            db.commit()
            return {"message": "Document updated successfully", "file_url": existing_doc.file_url}

    doc = models.Document(
        employee_id=employee_id,
        title=title,
        file_url=file_url_1,
        file_url_2=file_url_2,
        document_type=document_type,
        issue_date=i_date,
        expiry_date=e_date
    )
    db.add(doc)
    db.commit()
    return {"message": "Document uploaded successfully", "file_url": doc.file_url}

@router.delete("/{employee_id}/documents/{document_id}")
def delete_employee_document(employee_id: int, document_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_doc = db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.employee_id == employee_id
    ).first()
    
    if not db_doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    db.delete(db_doc)
    db.commit()
    return {"message": "Document deleted successfully"}

@router.post("/{employee_id}/remarks", response_model=schemas.RemarkResponse)
def add_remark(employee_id: int, remark: schemas.RemarkCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_emp = crud.get_employee(db, employee_id=employee_id)
    if not db_emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    new_remark = models.Remark(
        employee_id=employee_id,
        user_id=current_user.id,
        note=remark.note
    )
    db.add(new_remark)
    db.commit()
    db.refresh(new_remark)
    return new_remark

@router.delete("/{employee_id}/remarks/{remark_id}")
def delete_remark(employee_id: int, remark_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_remark = db.query(models.Remark).filter(
        models.Remark.id == remark_id,
        models.Remark.employee_id == employee_id
    ).first()
    
    if not db_remark:
        raise HTTPException(status_code=404, detail="Remark not found")
        
    db.delete(db_remark)
    db.commit()
    return {"message": "Remark deleted successfully"}
