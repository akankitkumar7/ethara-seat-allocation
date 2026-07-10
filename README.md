<<<<<<< HEAD
# Ethara Seat Allocation & Project Mapping System

A full-stack internal operations tool for mapping employees to projects and physical seats. It uses a FastAPI REST API, SQLAlchemy models portable between SQLite and PostgreSQL, and a responsive React/Tailwind dashboard.

## What is included

- Employee CRUD, including soft deactivation and database-enforced unique email/code constraints.
- Project management and seeded Ethara project names.
- Seat inventory, seat status filters, location uniqueness, suggested seat ranking, allocation, and release.
- Transactional rules that prevent a seat or employee having more than one active allocation.
- Live dashboard summary, project allocation, floor occupancy, and pending joiner count.
- A database-backed, rule-based assistant at `POST /ai/query`.
- Re-runnable seed script for 5,000 employees and 5,500 seats.

## Run locally

Use Python 3.11+ and Node.js 20+.

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python scripts/seed_data.py
uvicorn app.main:app --reload
```

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`; FastAPI Swagger documentation is at `http://localhost:8000/docs`.

## Integrity design

The allocation service verifies that the employee is active and unallocated, then that the target seat is `Available`, creates the allocation and marks the seat `Occupied` in one commit. Partial unique indexes on active `seat_allocations` backstop concurrent requests: one active employee allocation and one active seat allocation are possible. Releasing records a release time and returns the seat to `Available` in the same transaction. Reserved and maintenance seats cannot be allocated.

For a PostgreSQL deployment, set `DATABASE_URL` in `backend/app/database.py` (or wire it to environment configuration) to a PostgreSQL SQLAlchemy URL and use Alembic migrations. Authentication, authorization, auditing, request rate limiting, stronger connection-pool settings, and structured observability are the main additions recommended before a public production deployment.
=======
# Ethara-Seat-Allocation-Project-Mapping-System
>>>>>>> fd45a75bd4b21ffca2277e31cd4009cc807d877c
