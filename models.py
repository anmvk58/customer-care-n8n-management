from database import Base
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True)
    username = Column(String(50), unique=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    hashed_password = Column(String(150))
    role = Column(String(50))
    department = Column(String(100))
    phone_number = Column(String(15), unique=True)
    is_active = Column(Boolean, default=True)
    create_at = Column(TIMESTAMP, server_default=func.now())

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class CompanyEventScheduler(Base):
    __tablename__ = "company_event_scheduler"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(200))
    event_day = Column(Integer)
    event_month = Column(Integer)
    event_year = Column(Integer)
    event_type = Column(String(50))
    event_object = Column(String(100))
    event_title = Column(String(100))
    event_position = Column(String(100))
    promt = Column(String(255))
    received_email = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_loop = Column(Boolean, default=True)
    create_time = Column(TIMESTAMP, server_default=func.now())

    @property
    def full_event(self):
        return f"{self.event_day}-{self.event_month}-{self.event_year}"
