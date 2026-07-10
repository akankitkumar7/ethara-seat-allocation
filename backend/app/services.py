from collections import Counter
from datetime import datetime
import re
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from .models import AllocationStatus, Employee, EmployeeStatus, Project, Seat, SeatAllocation, SeatStatus

def active_allocation_for_employee(db: Session, employee_id: int):
    return db.scalar(select(SeatAllocation).where(SeatAllocation.employee_id == employee_id, SeatAllocation.allocation_status == AllocationStatus.ACTIVE))

def allocate_seat(db: Session, employee_id: int, seat_id: int):
    employee = db.get(Employee, employee_id)
    seat = db.get(Seat, seat_id)
    if not employee or employee.status != EmployeeStatus.ACTIVE: raise ValueError("Employee must exist and be active")
    if not seat: raise ValueError("Seat not found")
    if active_allocation_for_employee(db, employee_id): raise ValueError("Employee already has an active seat allocation")
    if seat.status != SeatStatus.AVAILABLE: raise ValueError(f"Seat is {seat.status.value} and cannot be allocated")
    allocation = SeatAllocation(employee_id=employee.id, seat_id=seat.id, project_id=employee.project_id)
    seat.status = SeatStatus.OCCUPIED
    db.add(allocation)
    try: db.commit()
    except IntegrityError:
        db.rollback(); raise ValueError("Seat or employee was allocated by another request; refresh and try again")
    db.refresh(allocation); return allocation

def release_seat(db: Session, employee_id: int | None, seat_id: int | None):
    if not employee_id and not seat_id: raise ValueError("Provide employee_id or seat_id")
    query = select(SeatAllocation).where(SeatAllocation.allocation_status == AllocationStatus.ACTIVE)
    if employee_id: query = query.where(SeatAllocation.employee_id == employee_id)
    if seat_id: query = query.where(SeatAllocation.seat_id == seat_id)
    allocation = db.scalar(query)
    if not allocation: raise ValueError("No active allocation found")
    allocation.allocation_status = AllocationStatus.RELEASED; allocation.released_date = datetime.utcnow(); allocation.seat.status = SeatStatus.AVAILABLE
    db.commit(); return allocation

def suggest_seats(db: Session, employee: Employee, limit: int = 8):
    teammate_zones = select(Seat.floor, Seat.zone, func.count(Seat.id).label("team_count")).join(SeatAllocation).where(SeatAllocation.project_id == employee.project_id, SeatAllocation.allocation_status == AllocationStatus.ACTIVE).group_by(Seat.floor, Seat.zone).subquery()
    return db.scalars(select(Seat).outerjoin(teammate_zones, (Seat.floor == teammate_zones.c.floor) & (Seat.zone == teammate_zones.c.zone)).where(Seat.status == SeatStatus.AVAILABLE).order_by(teammate_zones.c.team_count.desc().nullslast(), Seat.floor, Seat.zone, Seat.bay, Seat.seat_number).limit(limit)).all()

def assistant_answer(db: Session, query: str) -> str:
    q = query.lower().strip()
    if any(x in q for x in ["available seat", "free seat"]):
        floor_match = re.search(r"\bfloor\s*(\d+)", q)
        floor = int(floor_match.group(1)) if floor_match else None
        stmt = select(Seat).where(Seat.status == SeatStatus.AVAILABLE)
        if floor: stmt = stmt.where(Seat.floor == floor)
        seats = db.scalars(stmt.order_by(Seat.floor, Seat.zone).limit(10)).all()
        scope = f" on Floor {floor}" if floor else ""
        return f"There are {len(seats)} available seats shown{scope}: " + ", ".join(f"F{s.floor} {s.zone}, {s.bay}, {s.seat_number}" for s in seats) if seats else f"No available seats found{scope}."
    project = db.scalar(select(Project).where(func.lower(Project.name).in_([word.strip('?.!,') for word in q.split()])))
    if project and any(x in q for x in ["how many", "occupied", "utilization"]):
        count = db.scalar(select(func.count()).select_from(SeatAllocation).where(SeatAllocation.project_id == project.id, SeatAllocation.allocation_status == AllocationStatus.ACTIVE))
        return f"Project {project.name} currently has {count} occupied seat(s)."
    matches: list[Employee] = []
    candidate = ""
    if any(x in q for x in ["where", "seated", "seat", "project", "assigned"]):
        candidate = re.sub(r"^(?:where\s+is|find|locate|show)(?:\s+employee)?\s+", "", q)
        candidate = re.sub(r"\s+(?:seated|sitting|sit|located|seat|project|assigned).*$", "", candidate).strip(" ?.!,")
        if candidate:
            # A complete name is exact; a single word is treated as a first-name lookup.
            if " " in candidate:
                matches = db.scalars(select(Employee).where(func.lower(Employee.name) == candidate)).all()
            else:
                # Include an exact one-word name ("Ankit") and full names that share
                # that first name ("Ankit Kumar") in the same response.
                matches = db.scalars(select(Employee).where(or_(
                    func.lower(Employee.name) == candidate,
                    func.lower(Employee.name).like(f"{candidate} %"),
                )).order_by(Employee.name)).all()
    if matches:
        def employee_detail(employee: Employee) -> str:
            allocation = active_allocation_for_employee(db, employee.id)
            if any(x in q for x in ["project", "assigned"]):
                return f"{employee.name} is assigned to Project {employee.project.name}."
            if allocation:
                s = allocation.seat
                return f"{employee.name} is seated on Floor {s.floor}, Zone {s.zone}, Bay {s.bay}, Seat {s.seat_number}. They are assigned to Project {employee.project.name}."
            return f"{employee.name} is assigned to Project {employee.project.name} and is currently pending seat allocation."
        if len(matches) == 1:
            return employee_detail(matches[0])
        return f"I found {len(matches)} employees named {candidate.title()}: " + " ".join(employee_detail(employee) for employee in matches)
    if candidate:
        return f"No employee named {candidate.title()} was found. Check the spelling or search from the Employees page."
    return "I can help with employee seat or project lookups, available seats by floor, and project occupancy. Try: ‘Where is employee Amit seated?’"
