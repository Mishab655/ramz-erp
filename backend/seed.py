import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import SessionLocal, engine
from app import models
from app.core.security import get_password_hash

def seed_data():
    db: Session = SessionLocal()
    
    # Create tables
    models.Base.metadata.create_all(bind=engine)
    
    # Check if user already exists
    if db.query(models.User).filter(models.User.email == "admin@ramzalwahda.com").first():
        print("Data already seeded.")
        return

    # Create admin user
    hashed_pw = get_password_hash("admin123")
    admin = models.User(email="admin@ramzalwahda.com", password_hash=hashed_pw, full_name="System Admin")
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    # Create branches
    b1 = models.Branch(name="AL-Sad")
    b2 = models.Branch(name="Swaihan-1")
    b3 = models.Branch(name="Swaihan-2")
    db.add_all([b1, b2, b3])
    db.commit()
    db.refresh(b1)
    db.refresh(b2)
    db.refresh(b3)
    
    # Create sample employees
    now = datetime.now()
    e1 = models.Employee(
        branch_id=b1.id, full_name="Ahmed Ali", place="Dubai", address="St 1", phone_number="0501234567",
        emirates_id="784-1234-1234567-1", emirates_id_expiry=now + timedelta(days=365),
        visa_date=now - timedelta(days=100), visa_expiry=now + timedelta(days=20),
        passport_number="P1234567", joined_date=now - timedelta(days=365),
        salary=5000, salary_pending=0
    )
    e2 = models.Employee(
        branch_id=b2.id, full_name="John Doe", place="Abu Dhabi", address="St 2", phone_number="0507654321",
        emirates_id="784-4321-7654321-1", emirates_id_expiry=now + timedelta(days=15),
        visa_date=now - timedelta(days=200), visa_expiry=now + timedelta(days=365),
        passport_number="P7654321", joined_date=now - timedelta(days=200),
        salary=6000, salary_pending=2000
    )
    db.add_all([e1, e2])
    db.commit()
    
    print("Database seeded successfully.")
    print("Login with email: admin@ramzalwahda.com | password: admin123")
    db.close()

if __name__ == "__main__":
    seed_data()
