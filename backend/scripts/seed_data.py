"""Rebuild a realistic local demo database. Run from backend/: python scripts/seed_data.py"""
import random
import sys
from datetime import date, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from faker import Faker
from app.database import Base, SessionLocal, engine
from app.models import AllocationStatus, Employee, EmployeeStatus, Project, ProjectStatus, Seat, SeatAllocation, SeatStatus

fake = Faker("en_IN")
PROJECTS = ["Indigo", "Indreed", "Mydreed", "Preed", "Serfy", "Oreed", "bedegreed", "Opreed", "Serry", "Kaary", "Mered"]
DEPARTMENTS = ["Engineering", "Growth", "Operations", "HR", "Finance", "Design", "Sales"]
ROLES = ["Analyst", "Executive", "Manager", "Engineer", "Specialist", "Lead"]

def run():
    Base.metadata.drop_all(engine); Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        projects = [Project(name=n, description=f"{n} delivery programme", manager_name=fake.name(), status=ProjectStatus.ACTIVE) for n in PROJECTS]
        db.add_all(projects); db.flush()
        seats=[]
        # 5 floors x 10 zones x 110 seats = 5,500 seats
        for floor in range(1, 6):
            for zone_num in range(1, 11):
                zone = chr(64 + zone_num)
                for number in range(1, 111):
                    bay = f"{zone}{(number - 1) // 22 + 1}"
                    seats.append(Seat(floor=floor, zone=zone, bay=bay, seat_number=f"{bay}-{number:03d}", status=SeatStatus.AVAILABLE))
        db.add_all(seats); db.flush()
        employees=[]
        for i in range(5000):
            employees.append(Employee(employee_code=f"ETH-{i+1001:05d}", name=fake.name(), email=f"ethara{i+1}@example.com", department=random.choice(DEPARTMENTS), role=random.choice(ROLES), joining_date=date.today()-timedelta(days=random.randint(0,1200)), status=EmployeeStatus.ACTIVE, project_id=random.choice(projects).id))
        db.add_all(employees); db.flush()
        # 4,850 occupied, 500 available, 100 reserved, 50 maintenance; 150 new joiners remain unallocated.
        assigned_seats=random.sample(seats, 4850)
        for seat, employee in zip(assigned_seats, employees[:4850]):
            seat.status=SeatStatus.OCCUPIED
            db.add(SeatAllocation(employee_id=employee.id, seat_id=seat.id, project_id=employee.project_id, allocation_status=AllocationStatus.ACTIVE))
        remaining=[s for s in seats if s not in assigned_seats]
        for seat in remaining[:100]: seat.status=SeatStatus.RESERVED
        for seat in remaining[100:150]: seat.status=SeatStatus.MAINTENANCE
        db.commit()
        print("Seeded 5,000 employees, 5,500 seats, 11 projects; 150 employees are pending allocation.")
    finally: db.close()
if __name__ == "__main__": run()
