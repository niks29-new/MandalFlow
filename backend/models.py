from sqlalchemy import Column, Integer, String
from backend.database import Base


# =====================================================
# MEMBERS
# =====================================================

class Member(Base):

    __tablename__ = "members"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    # Personal Details

    name = Column(
        String(100),
        nullable=False
    )


    mobile = Column(
        String(20),
        nullable=False
    )


    house_no = Column(
        String(50),
        default=""
    )


    area = Column(
        String(100),
        default=""
    )


    address = Column(
        String(255),
        default=""
    )



    # Collection Details


    expected_amount = Column(
        Integer,
        default=500
    )


    paid_amount = Column(
        Integer,
        default=0
    )


    status = Column(
        String(20),
        default="Pending"
    )


    payment_mode = Column(
        String(30),
        default=""
    )


    payment_date = Column(
        String(30),
        default=""
    )


    collected_by = Column(
        String(100),
        default=""
    )


    remarks = Column(
        String(255),
        default=""
    )



# =====================================================
# PAYMENTS
# =====================================================


class Payment(Base):

    __tablename__ = "payments"



    id = Column(
        Integer,
        primary_key=True,
        index=True
    )



    # Member Reference


    member_id = Column(
        Integer,
        nullable=False
    )



    # Contribution Details


    contribution_type = Column(
        String(50),
        default="Chanda"
    )


    # Rice packets / Laddu quantity

    quantity = Column(
        Integer,
        default=0
    )



    # Sponsor details

    sponsor_details = Column(
        String(255),
        default=""
    )



    # Payment Details


    amount = Column(
        Integer,
        nullable=False,
        default=0
    )


    payment_mode = Column(
        String(20),
        default="Cash"
    )


    payment_date = Column(
        String(30),
        default=""
    )


    next_payment_date = Column(
        String(30),
        default=""
    )



    # Committee Details


    received_by = Column(
        String(100),
        default=""
    )


    transaction_id = Column(
        String(100),
        default=""
    )


    remarks = Column(
        String(255),
        default=""
    )



# =====================================================
# EXPENSES
# =====================================================


class Expense(Base):

    __tablename__ = "expenses"



    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    expense_type = Column(
        String(100),
        nullable=False
    )


    amount = Column(
        Integer,
        nullable=False
    )


    payment_mode = Column(
        String(20),
        default="Cash"
    )


    paid_by = Column(
        String(100),
        default=""
    )


    category = Column(
        String(100),
        default="Others"
    )


    expense_date = Column(
        String(30),
        default=""
    )


    transaction_id = Column(
        String(100),
        default=""
    )


    remarks = Column(
        String(255),
        default=""
    )



# =====================================================
# ADMIN USERS
# =====================================================


class Admin(Base):

    __tablename__ = "admins"



    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    username = Column(
        String(50),
        unique=True,
        nullable=False
    )


    password = Column(
        String(255),
        nullable=False
    )