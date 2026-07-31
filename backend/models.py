from sqlalchemy import Column, Integer, String
from backend.database import Base


# =====================================================
# MEMBERS
# =====================================================

class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)

    # Personal Details
    name = Column(String, nullable=False)
    mobile = Column(String, nullable=False)

    house_no = Column(String)
    area = Column(String)
    address = Column(String)

    # Collection Details
    expected_amount = Column(Integer, default=500)
    paid_amount = Column(Integer, default=0)

    status = Column(String, default="Pending")

    payment_mode = Column(String)
    payment_date = Column(String)

    collected_by = Column(String)

    remarks = Column(String)


# =====================================================
# PAYMENTS
# =====================================================

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    member_id = Column(Integer, nullable=False)

    contribution_type = Column(String)

    amount = Column(Integer, nullable=False)

    # Cash / UPI
    payment_mode = Column(String, default="Cash")

    payment_date = Column(String)

    next_payment_date = Column(String)

    # Committee Member
    received_by = Column(String)

    # UPI Reference Number
    transaction_id = Column(String)

    remarks = Column(String)
    # =====================================================
# EXPENSES
# =====================================================

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)

    # Expense Details
    expense_type = Column(String, nullable=False)

    amount = Column(Integer, nullable=False)

    # Cash / UPI
    payment_mode = Column(String, default="Cash")

    # Committee Member who paid
    paid_by = Column(String)

    # Expense Category
    # Example:
    # Decoration
    # DJ
    # Food
    # Prasad
    # Electrical
    # Transport
    # Others
    category = Column(String)

    expense_date = Column(String)

    # UPI Transaction Reference
    transaction_id = Column(String)

    remarks = Column(String)


# =====================================================
# ADMIN USERS
# =====================================================

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(
        String,
        unique=True,
        nullable=False
    )

    password = Column(
        String,
        nullable=False
    )