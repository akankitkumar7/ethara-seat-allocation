# 🚀 Ethara Seat Allocation & Project Mapping System

A full-stack web application designed to efficiently manage **seat allocation**, **employee-project mapping**, and **workspace utilization** for organizations with approximately **5,000+ employees**.

The system enables HR, Admin, Project Managers, and Employees to manage seating assignments, monitor workspace utilization, allocate seats for new joiners, and retrieve information through an AI-powered natural language assistant.

---

## 🌐 Live Demo

### Frontend
https://ethara-seat-allocation-pearl.vercel.app

### Backend
https://ethara-backend-4jjh.onrender.com

### API Documentation (Swagger)
https://ethara-backend-4jjh.onrender.com/docs

---

# ✨ Features

## 👨‍💼 Employee Management

- Create Employee
- View Employee Details
- Automatic Employee Code Generation
- Unique Email Validation

---

## 📁 Project Management

- Multiple Active Projects
- Employee-to-Project Mapping
- View Employees by Project
- Project-wise Seat Allocation

---

## 💺 Seat Management

- View All Seats
- Filter Seats
- Available Seats
- Reserved Seats
- Maintenance Seats
- Occupied Seats

---

## 🔄 Seat Allocation

- Allocate Seat
- Automatic Seat Status Updates
- Duplicate Seat Allocation Prevention
- One Active Seat per Employee
- One Employee per Seat

---

## 🆕 New Joiner Workflow

- Register New Employee
- Select Active Project
- Automatic Seat Suggestions
- Allocate Seat
- Instant Dashboard Update

---

## 🔍 Search & Filters

Search employees by:

- Employee Name
- Employee Code
- Email
- Project
- Floor
- Zone
- Seat Status

Supports multiple filters simultaneously.

---

## 📊 Dashboard & Analytics

Real-time dashboard displaying:

- Total Employees
- Total Seats
- Occupied Seats
- Available Seats
- Reserved Seats
- Pending Allocations
- Project-wise Utilization
- Floor-wise Occupancy

---

## 🤖 AI Assistant

Natural Language Query Interface supporting questions such as:

- Where is Ankit seated?
- Which project is Rahul assigned to?
- Show available seats on Floor 3.
- How many seats are occupied?
- Allocate seat for a new employee.

The assistant is implemented using a lightweight rule-based NLP engine backed by real database queries.

---

# 🛠️ Tech Stack

## Frontend

- React.js
- Vite
- Tailwind CSS
- TypeScript

## Backend

- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn

## Database

- SQLite
- Faker (Seed Data)

## Deployment

- Frontend → Vercel
- Backend → Render

---

# 🗄️ Database Design

The application consists of four primary entities:

- Employees
- Projects
- Seats
- Seat Allocations

### Relationships

- One Project → Many Employees
- One Employee → One Active Seat Allocation
- One Seat → One Active Employee
- Seat Allocation acts as the mapping table.

---

# 🌱 Seed Data

The project includes an automatic seed script that generates realistic demo data.

Generated dataset includes:

| Data | Count |
|-------|------:|
| Employees | 5,000 |
| Projects | 11 |
| Floors | 5 |
| Zones | 10 |
| Seats | 5,500 |
| Occupied Seats | 4,850 |
| Available Seats | 500 |
| Reserved Seats | 100 |
| Maintenance Seats | 50 |
| Pending Allocations | 150 |

The database is automatically seeded on the first application startup if no employee records exist.

---

# 📡 REST APIs

## Employees

- POST `/employees`
- GET `/employees`
- GET `/employees/{id}`
- PUT `/employees/{id}`
- DELETE `/employees/{id}`

---

## Projects

- POST `/projects`
- GET `/projects`
- GET `/projects/{id}/employees`

---

## Seats

- POST `/seats`
- GET `/seats`
- GET `/seats/available`
- POST `/seats/allocate`
- POST `/seats/release`

---

## Dashboard

- GET `/dashboard/summary`
- GET `/dashboard/project-utilization`
- GET `/dashboard/floor-utilization`

---

## AI Assistant

- POST `/ai/query`

---

# 🧠 Business Rules Implemented

The backend enforces the following rules:

- One employee can have only one active seat.
- One seat can be assigned to only one employee.
- Duplicate employee emails are prevented.
- Duplicate seat numbers are prevented.
- Reserved seats cannot be allocated.
- Released seats immediately become available.
- Dashboard updates immediately after allocation/release.
- New joiners receive seat suggestions based on project proximity.

---

# 🌍 Deployment

| Component | Platform |
|-----------|----------|
| Frontend | Vercel |
| Backend | Render |
| Database | SQLite |

Environment Variables:

Frontend

```
VITE_API_URL=https://ethara-backend-4jjh.onrender.com
```

---

# 📸 Screenshots

The following screenshots demonstrate the application's major features.

- Dashboard
- Employee Management
- Seat Management
- New Joiner Registration
- AI Assistant
- Search & Filters

<img width="1917" height="938" alt="dashboard" src="https://github.com/user-attachments/assets/0c5b7d1f-12e4-44a3-90ba-3e79efe594cd" />
<img width="1918" height="941" alt="employees" src="https://github.com/user-attachments/assets/278ae149-7aea-414a-a528-9a38c5ad136b" />
<img width="1918" height="933" alt="new-joinee" src="https://github.com/user-attachments/assets/95dd0860-b703-48f0-a3e2-d363940a72fb" />
> <img width="1918" height="937" alt="seats" src="https://github.com/user-attachments/assets/26a8702c-f081-4f9a-a9ff-bc57980d0405" />
<img width="1918" height="938" alt="assistance" src="https://github.com/user-attachments/assets/ec0c387b-1cc1-416d-8f4f-000aa6de7406" />



---

# 🔮 Future Improvements

Possible production enhancements include:

- PostgreSQL
- Authentication & Authorization
- Role-Based Access Control (RBAC)
- Real-time Notifications
- Email Notifications
- Bulk Employee Upload
- CSV Import/Export
- Audit Logs
- Docker Support
- CI/CD Pipeline
- Redis Caching

---

# 📄 AI Usage

AI-assisted development was used throughout this project.

Detailed documentation is available in:

```
AI_PROMPTS.md
```

The objective was to build a scalable full-stack application capable of managing seat allocation, project mapping, workspace utilization, analytics, and AI-assisted querying for approximately 5,000 employees.
