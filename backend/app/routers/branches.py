from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, database, models
from .auth import get_current_user

router = APIRouter(prefix="/branches", tags=["Branches"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas.BranchResponse])
def read_branches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    branches = crud.get_branches(db, skip=skip, limit=limit)
    return branches

@router.post("/", response_model=schemas.BranchResponse)
def create_branch(branch: schemas.BranchCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_branch(db=db, branch=branch)

@router.get("/{branch_id}", response_model=schemas.BranchResponse)
def read_branch(branch_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_branch = crud.get_branch(db, branch_id=branch_id)
    if db_branch is None:
        raise HTTPException(status_code=404, detail="Branch not found")
    return db_branch

@router.put("/{branch_id}", response_model=schemas.BranchResponse)
def update_branch(branch_id: int, branch: schemas.BranchUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_branch = crud.update_branch(db, branch_id=branch_id, branch=branch)
    if not db_branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return db_branch

@router.delete("/{branch_id}")
def delete_branch(branch_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    success = crud.delete_branch(db, branch_id=branch_id)
    if not success:
        raise HTTPException(status_code=404, detail="Branch not found")
    return {"message": "Branch deleted successfully"}
