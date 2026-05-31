from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import crud, database, models
from .auth import get_current_user

router = APIRouter(tags=["Dashboard"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/dashboard/stats")
def get_stats(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_dashboard_stats(db)

@router.get("/dashboard/alerts")
def get_alerts(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    from datetime import datetime, timedelta
    thirty_days_from_now = datetime.now() + timedelta(days=30)
    
    expiring_docs = db.query(models.Document).join(models.Employee).filter(
        models.Document.expiry_date <= thirty_days_from_now,
        models.Employee.is_deleted == False
    ).all()
    
    alerts = []
    for doc in expiring_docs:
        alerts.append({
            "employee_id": doc.employee_id,
            "employee_name": doc.employee.full_name,
            "document_type": doc.document_type,
            "title": doc.title,
            "expiry_date": doc.expiry_date
        })
    
    return {"alerts": alerts}

@router.get("/dashboard/documents_expiry")
def get_documents_expiry(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    from datetime import datetime, timedelta
    sixty_days_from_now = datetime.now() + timedelta(days=60)
    
    expiring_docs = db.query(models.Document).join(models.Employee).filter(
        models.Document.expiry_date <= sixty_days_from_now,
        models.Employee.is_deleted == False
    ).all()
    
    docs_by_type = {
        "Passport": [],
        "Insurance": [],
        "Visa": [],
        "Emirates ID": [],
        "Labour Card": [],
        "Other": []
    }

    for doc in expiring_docs:
        doc_type = doc.document_type if doc.document_type in docs_by_type else "Other"
        docs_by_type[doc_type].append({
            "employee_id": doc.employee_id,
            "employee_name": doc.employee.full_name,
            "title": doc.title,
            "issue_date": doc.issue_date,
            "expiry_date": doc.expiry_date
        })
    
    return docs_by_type
