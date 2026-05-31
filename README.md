# Ramz Al Wahda - Employee Management System

![Dashboard Preview](frontend/assets/logo.png)

A modern, cloud-ready Enterprise Resource Planning (ERP) web application tailored for internal employee management. Ramz Al Wahda provides an intuitive interface for tracking employee details, branch assignments, and critical document expiries.

## 🚀 Features

*   **Comprehensive Dashboard**: At-a-glance analytics showing total employees, branches, and upcoming document expiries.
*   **Document Management**: Upload and track Passports, Visas, Emirates IDs, Labour Cards, Insurance, and custom documents.
*   **Smart Expiry Alerts**: Visual warnings (red highlights) for documents expiring within the next 60 days.
*   **Branch Management**: Easily assign and track employees across different corporate branches.
*   **Secure Authentication**: JWT-based login system with Bcrypt password hashing.
*   **Cloud Storage Integration**: Seamless uploading of employee photos and documents directly to Supabase cloud buckets.

## 🛠️ Technology Stack

**Frontend**
*   Vanilla HTML5 / JavaScript (ES6)
*   Tailwind CSS (via CDN) for rapid, responsive UI design
*   Font Awesome for modern iconography
*   Chart.js for interactive dashboard data visualizations

**Backend**
*   **FastAPI**: High-performance asynchronous Python web framework
*   **SQLAlchemy**: Robust Object Relational Mapper (ORM)
*   **PostgreSQL**: Cloud-hosted relational database (via Supabase)
*   **Python-JOSE & Passlib**: For secure JWT authentication

**Cloud & Deployment**
*   **Vercel**: Global CDN hosting for the frontend
*   **Render**: Web Service hosting for the FastAPI backend
*   **Supabase**: Managed PostgreSQL database and Cloud Storage buckets

## 💻 Local Development Setup

To run this project locally on your machine, follow these steps:

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR-USERNAME/ramz-erp.git
cd ramz-erp
```

### 2. Backend Setup
Make sure you have Python 3.11+ installed.

```bash
# Navigate to the root folder
cd ramz-erp

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory of the project and add your Supabase credentials:

```env
DATABASE_URL=postgresql://your-db-user:your-password@your-pooler.supabase.com:6543/postgres
SUPABASE_URL=https://your-project-url.supabase.co
SUPABASE_KEY=your-anon-or-service-key
```

### 4. Run the Servers

**Start the Backend API:**
```bash
uvicorn backend.app.main:app --reload --port 8000
```
*The API will be available at `http://localhost:8000`*
*Interactive API documentation will be available at `http://localhost:8000/docs`*

**Start the Frontend UI:**
You can use any live server extension (like VS Code's Live Server) to open `frontend/index.html`, or run a simple Python server:
```bash
cd frontend
python -m http.server 5500
```
*The website will be available at `http://localhost:5500`*

## 📦 Deployment Architecture
*   The frontend dynamically checks its hostname. If it's on Vercel, it routes all API traffic to the live Render backend. If on `localhost`, it routes to your local `uvicorn` instance.
*   File uploads are configured to pipe directly to a public Supabase bucket named `ramz-uploads`.

---
*Built for Ramz Al Wahda Group.*
