from datetime import date
from app.database import Base, SessionLocal, engine
from app.models import Employee, Project, Seat, SeatStatus
from app.services import allocate_seat, release_seat

def test_no_double_allocation_and_release():
    Base.metadata.drop_all(engine); Base.metadata.create_all(engine)
    db=SessionLocal()
    try:
        project=Project(name="Test Project"); db.add(project); db.flush()
        e1=Employee(employee_code="E1",name="One",email="one@test.com",department="IT",role="Dev",joining_date=date.today(),project_id=project.id)
        e2=Employee(employee_code="E2",name="Two",email="two@test.com",department="IT",role="Dev",joining_date=date.today(),project_id=project.id)
        seat=Seat(floor=1,zone="A",bay="A1",seat_number="A1-001")
        db.add_all([e1,e2,seat]);db.commit()
        allocate_seat(db,e1.id,seat.id)
        assert db.get(Seat,seat.id).status == SeatStatus.OCCUPIED
        try: allocate_seat(db,e2.id,seat.id); assert False
        except ValueError: pass
        release_seat(db,e1.id,None)
        assert db.get(Seat,seat.id).status == SeatStatus.AVAILABLE
    finally: db.close()
