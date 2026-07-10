from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from .database import Base, engine, get_db
from .models import AllocationStatus, Employee, EmployeeStatus, Project, Seat, SeatAllocation, SeatStatus
from .schemas import *
from .services import active_allocation_for_employee, allocate_seat, assistant_answer, release_seat, suggest_seats

Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Ethara Seat Allocation & Project Mapping System", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://ethara-seat-allocation-pearl.vercel.app",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


def fail(e): raise HTTPException(status_code=400, detail=str(e))


@app.post("/projects", response_model=ProjectOut, status_code=201)
def create_project(body: ProjectCreate, db: Session = Depends(get_db)):
    try:
        p = Project(**body.model_dump())
        db.add(p)
        db.commit()
        db.refresh(p)
        return p
    except IntegrityError:
        db.rollback()
        fail("Project name already exists")


@app.get("/projects", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)): return db.scalars(
    select(Project).order_by(Project.name)).all()


@app.get("/projects/{project_id}/employees", response_model=list[EmployeeOut])
def project_employees(project_id: int, db: Session = Depends(get_db)): return db.scalars(select(Employee).options(joinedload(
    Employee.project)).where(Employee.project_id == project_id, Employee.status == EmployeeStatus.ACTIVE)).unique().all()


@app.post("/employees", response_model=EmployeeOut, status_code=201)
def create_employee(body: EmployeeCreate, db: Session = Depends(get_db)):
    project = db.get(Project, body.project_id)
    if not project or project.status.value != "active":
        fail("Active project not found")
    data = body.model_dump()
    data["email"] = str(data["email"])
    data["employee_code"] = data[
        "employee_code"] or f"ETH-{db.scalar(select(func.count(Employee.id))) + 1001:05d}"
    try:
        e = Employee(**data)
        db.add(e)
        db.commit()
        db.refresh(e)
        return e
    except IntegrityError:
        db.rollback()
        fail("Employee email or employee code already exists")


@app.get("/employees", response_model=list[EmployeeOut])
def list_employees(skip: int = 0, limit: int = Query(50, le=200), search: str | None = None, project_id: int | None = None, floor: int | None = None, zone: str | None = None, seat_status: SeatStatus | None = None, db: Session = Depends(get_db)):
    stmt = select(Employee).options(joinedload(Employee.project)
                                    ).where(Employee.status == EmployeeStatus.ACTIVE)
    if search:
        stmt = stmt.where((Employee.name.ilike(f"%{search}%")) | (Employee.email.ilike(
            f"%{search}%")) | (Employee.employee_code.ilike(f"%{search}%")))
    if project_id:
        stmt = stmt.where(Employee.project_id == project_id)
    if floor or zone or seat_status:
        stmt = stmt.join(SeatAllocation, Employee.id == SeatAllocation.employee_id, isouter=True).join(
            Seat, SeatAllocation.seat_id == Seat.id, isouter=True)
        if floor:
            stmt = stmt.where(Seat.floor == floor)
        if zone:
            stmt = stmt.where(Seat.zone == zone)
        if seat_status:
            stmt = stmt.where(Seat.status == seat_status)
    return db.scalars(stmt.offset(skip).limit(limit)).unique().all()


@app.get("/employees/{employee_id}", response_model=EmployeeOut)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    e = db.scalar(select(Employee).options(joinedload(
        Employee.project)).where(Employee.id == employee_id))
    if not e:
        raise HTTPException(404, "Employee not found")
    return e


@app.put("/employees/{employee_id}", response_model=EmployeeOut)
def update_employee(employee_id: int, body: EmployeeUpdate, db: Session = Depends(get_db)):
    e = db.get(Employee, employee_id)
    if not e:
        raise HTTPException(404, "Employee not found")
    changes = body.model_dump(exclude_unset=True)
    if "project_id" in changes:
        project = db.get(Project, changes["project_id"])
        if not project or project.status.value != "active":
            fail("Active project not found")
    for k, v in changes.items():
        setattr(e, k, str(v) if k == "email" else v)
    try:
        db.commit()
        db.refresh(e)
        return e
    except IntegrityError:
        db.rollback()
        fail("Email already exists")


@app.delete("/employees/{employee_id}")
def deactivate_employee(employee_id: int, db: Session = Depends(get_db)):
    e = db.get(Employee, employee_id)
    if not e:
        raise HTTPException(404, "Employee not found")
    if active_allocation_for_employee(db, e.id):
        release_seat(db, e.id, None)
    e.status = EmployeeStatus.INACTIVE
    db.commit()
    return {"message": "Employee deactivated"}


@app.get("/employees/{employee_id}/seat-suggestions", response_model=list[SeatOut])
def employee_suggestions(employee_id: int, db: Session = Depends(get_db)):
    e = db.get(Employee, employee_id)
    if not e:
        raise HTTPException(404, "Employee not found")
    return suggest_seats(db, e)


@app.post("/seats", response_model=SeatOut, status_code=201)
def create_seat(body: SeatCreate, db: Session = Depends(get_db)):
    try:
        s = Seat(**body.model_dump())
        db.add(s)
        db.commit()
        db.refresh(s)
        return s
    except IntegrityError:
        db.rollback()
        fail("Duplicate seat number in this floor and zone")


@app.get("/seats", response_model=list[SeatOut])
def list_seats(floor: int | None = None, zone: str | None = None, status: SeatStatus | None = None, project_id: int | None = None, db: Session = Depends(get_db)):
    stmt = select(Seat)
    if floor:
        stmt = stmt.where(Seat.floor == floor)
    if zone:
        stmt = stmt.where(Seat.zone == zone)
    if status:
        stmt = stmt.where(Seat.status == status)
    if project_id:
        stmt = stmt.join(SeatAllocation).where(SeatAllocation.project_id ==
                                               project_id, SeatAllocation.allocation_status == AllocationStatus.ACTIVE)
    return db.scalars(stmt.order_by(Seat.floor, Seat.zone, Seat.seat_number)).all()


@app.get("/seats/available", response_model=list[SeatOut])
def available_seats(floor: int | None = None, zone: str | None = None, db: Session = Depends(
    get_db)): return list_seats(floor, zone, SeatStatus.AVAILABLE, None, db)


@app.post("/seats/allocate", response_model=AllocationOut)
def allocate(body: AllocateRequest, db: Session = Depends(get_db)):
    try:
        return allocate_seat(db, body.employee_id, body.seat_id)
    except ValueError as e:
        fail(e)


@app.post("/seats/release", response_model=AllocationOut)
def release(body: ReleaseRequest, db: Session = Depends(get_db)):
    try:
        return release_seat(db, body.employee_id, body.seat_id)
    except ValueError as e:
        fail(e)


@app.get("/dashboard/summary")
def summary(db: Session = Depends(get_db)):
    def seats(status): return db.scalar(
        select(func.count()).select_from(Seat).where(Seat.status == status))
    pending = db.scalar(select(func.count()).select_from(Employee).where(Employee.status == EmployeeStatus.ACTIVE, ~Employee.id.in_(
        select(SeatAllocation.employee_id).where(SeatAllocation.allocation_status == AllocationStatus.ACTIVE))))
    return {"total_employees": db.scalar(select(func.count()).select_from(Employee).where(Employee.status == EmployeeStatus.ACTIVE)), "total_seats": db.scalar(select(func.count()).select_from(Seat)), "occupied_seats": seats(SeatStatus.OCCUPIED), "available_seats": seats(SeatStatus.AVAILABLE), "reserved_seats": seats(SeatStatus.RESERVED), "pending_allocation": pending}


@app.get("/dashboard/project-utilization")
def project_utilization(db: Session = Depends(get_db)):
    return [{"project": n, "occupied": c} for n, c in db.execute(select(Project.name, func.count(SeatAllocation.id)).outerjoin(SeatAllocation, (Project.id == SeatAllocation.project_id) & (SeatAllocation.allocation_status == AllocationStatus.ACTIVE)).group_by(Project.name).order_by(Project.name)).all()]


@app.get("/dashboard/floor-utilization")
def floor_utilization(db: Session = Depends(get_db)):
    return [{"floor": f, "total": t, "occupied": o} for f, t, o in db.execute(select(Seat.floor, func.count(Seat.id), func.sum(__import__('sqlalchemy').case((Seat.status == SeatStatus.OCCUPIED, 1), else_=0))).group_by(Seat.floor).order_by(Seat.floor)).all()]


@app.post("/ai/query", response_model=AssistantAnswer)
def ai_query(body: AssistantQuery, db: Session = Depends(get_db)): return {
    "answer": assistant_answer(db, body.query)}


@app.get("/health")
def health(): return {"status": "ok"}
