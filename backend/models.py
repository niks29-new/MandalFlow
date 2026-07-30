from sqlalchemy import Column, Integer, String
from backend.database import Base


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    mobile = Column(String, nullable=False)

    house_no = Column(String)
    area = Column(String)
    address = Column(String)

    expected_amount = Column(Integer, default=500)
    paid_amount = Column(Integer, default=0)

    status = Column(String, default="Pending")

    payment_mode = Column(String)
    payment_date = Column(String)

    collected_by = Column(String)

    remarks = Column(String)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    member_id = Column(Integer, nullable=False)

    contribution_type = Column(String)

    amount = Column(Integer)

    payment_mode = Column(String)

    payment_date = Column(String)

    next_payment_date = Column(String)

    received_by = Column(String)

    remarks = Column(String)
    