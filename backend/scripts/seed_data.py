"""Seed demo data for Ethara.

Safe to run multiple times.
If employees already exist, seeding is skipped.
"""

import random
import sys
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import Base, SessionLocal, engine
from app.models import (
    AllocationStatus,
    Employee,
    EmployeeStatus,
    Project,
    ProjectStatus,
    Seat,
    SeatAllocation,
    SeatStatus,
)

fake = Faker("en_IN")

PROJECTS = [
    "Indigo",
    "Indreed",
    "Mydreed",
    "Preed",
    "Serfy",
    "Oreed",
    "Bedegreed",
    "Opreed",
    "Serry",
    "Kaary",
    "Mered",
]

DEPARTMENTS = [
    "Engineering",
    "Growth",
    "Operations",
    "HR",
    "Finance",
    "Design",
    "Sales",
]

ROLES = [
    "Analyst",
    "Executive",
    "Manager",
    "Engineer",
    "Specialist",
    "Lead",
]


def run():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Prevent duplicate seeding
        if db.query(Employee).count() > 0:
            print("Database already contains data. Skipping seed.")
            return

        print("Database empty. Generating demo data...")

        # -----------------------------
        # Create Projects
        # -----------------------------
        projects = []

        for name in PROJECTS:
            project = Project(
                name=name,
                description=f"{name} delivery programme",
                manager_name=fake.name(),
                status=ProjectStatus.ACTIVE,
            )

            projects.append(project)

        db.add_all(projects)
        db.flush()

        # -----------------------------
        # Create Seats (5500)
        # -----------------------------
        seats = []

        for floor in range(1, 6):
            for zone_number in range(1, 11):

                zone = chr(64 + zone_number)

                for number in range(1, 111):

                    bay = f"{zone}{(number - 1) // 22 + 1}"

                    seat = Seat(
                        floor=floor,
                        zone=zone,
                        bay=bay,
                        seat_number=f"{bay}-{number:03d}",
                        status=SeatStatus.AVAILABLE,
                    )

                    seats.append(seat)

        db.add_all(seats)
        db.flush()

        # -----------------------------
        # Create Employees (5000)
        # -----------------------------
        employees = []

        for i in range(5000):

            employee = Employee(
                employee_code=f"ETH-{1001+i:05d}",
                name=fake.name(),
                email=f"ethara{i+1}@example.com",
                department=random.choice(DEPARTMENTS),
                role=random.choice(ROLES),
                joining_date=date.today()
                - timedelta(days=random.randint(0, 1200)),
                status=EmployeeStatus.ACTIVE,
                project_id=random.choice(projects).id,
            )

            employees.append(employee)

        db.add_all(employees)
        db.flush()

        # -----------------------------
        # Seat Allocation
        # -----------------------------
        assigned_seats = random.sample(seats, 4850)

        for seat, employee in zip(assigned_seats, employees[:4850]):

            seat.status = SeatStatus.OCCUPIED

            allocation = SeatAllocation(
                employee_id=employee.id,
                seat_id=seat.id,
                project_id=employee.project_id,
                allocation_status=AllocationStatus.ACTIVE,
            )

            db.add(allocation)

        # Remaining seats
        remaining = [seat for seat in seats if seat not in assigned_seats]

        # Reserved
        for seat in remaining[:100]:
            seat.status = SeatStatus.RESERVED

        # Maintenance
        for seat in remaining[100:150]:
            seat.status = SeatStatus.MAINTENANCE

        db.commit()

        print("=" * 60)
        print("Demo database generated successfully!")
        print("Projects   : 11")
        print("Employees  : 5000")
        print("Seats      : 5500")
        print("Allocated  : 4850")
        print("Reserved   : 100")
        print("Maintenance: 50")
        print("Available  : 500")
        print("Pending    : 150")
        print("=" * 60)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    run()