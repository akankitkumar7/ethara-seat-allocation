from datetime import date, datetime
from enum import Enum
from sqlalchemy import Date, DateTime, Enum as SqlEnum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class EmployeeStatus(str, Enum): ACTIVE = "active"; INACTIVE = "inactive"
class ProjectStatus(str, Enum): ACTIVE = "active"; INACTIVE = "inactive"
class SeatStatus(str, Enum): AVAILABLE = "Available"; OCCUPIED = "Occupied"; RESERVED = "Reserved"; MAINTENANCE = "Maintenance"
class AllocationStatus(str, Enum): ACTIVE = "active"; RELEASED = "released"

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    manager_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(SqlEnum(ProjectStatus), default=ProjectStatus.ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    employees: Mapped[list["Employee"]] = relationship(back_populates="project")

class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True)
    employee_code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    department: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(120))
    joining_date: Mapped[date] = mapped_column(Date)
    status: Mapped[EmployeeStatus] = mapped_column(SqlEnum(EmployeeStatus), default=EmployeeStatus.ACTIVE)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    project: Mapped[Project] = relationship(back_populates="employees")
    allocations: Mapped[list["SeatAllocation"]] = relationship(back_populates="employee")

class Seat(Base):
    __tablename__ = "seats"
    __table_args__ = (Index("uq_seat_location", "floor", "zone", "seat_number", unique=True),)
    id: Mapped[int] = mapped_column(primary_key=True)
    floor: Mapped[int] = mapped_column(Integer, index=True)
    zone: Mapped[str] = mapped_column(String(20), index=True)
    bay: Mapped[str] = mapped_column(String(30))
    seat_number: Mapped[str] = mapped_column(String(40), index=True)
    status: Mapped[SeatStatus] = mapped_column(SqlEnum(SeatStatus), default=SeatStatus.AVAILABLE, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    allocations: Mapped[list["SeatAllocation"]] = relationship(back_populates="seat")

class SeatAllocation(Base):
    __tablename__ = "seat_allocations"
    __table_args__ = (Index("uq_active_employee", "employee_id", unique=True, sqlite_where=(__import__('sqlalchemy').text("allocation_status = 'ACTIVE'"))), Index("uq_active_seat", "seat_id", unique=True, sqlite_where=(__import__('sqlalchemy').text("allocation_status = 'ACTIVE'"))),)
    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True)
    seat_id: Mapped[int] = mapped_column(ForeignKey("seats.id"), index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    allocation_status: Mapped[AllocationStatus] = mapped_column(SqlEnum(AllocationStatus), default=AllocationStatus.ACTIVE, index=True)
    allocation_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    released_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    employee: Mapped[Employee] = relationship(back_populates="allocations")
    seat: Mapped[Seat] = relationship(back_populates="allocations")
    project: Mapped[Project] = relationship()
