from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from . import models
from .database import engine
from .routers import auth, branches, employees, dashboard

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ramz Al Wahda Employee Management API")

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "https://ramz-erp.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory to serve static files
import os
os.makedirs("backend/uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="backend/uploads"), name="uploads")

# Include routers
app.include_router(auth.router, prefix="/api/auth")
app.include_router(dashboard.router, prefix="/api")
app.include_router(branches.router, prefix="/api")
app.include_router(employees.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to Ramz Al Wahda API"}
