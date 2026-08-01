# =====================================================
# KN STREET CHA RAJA
# Digital Chanda Management System
# Version 3.0
# =====================================================

from datetime import date
import os

from fastapi import (
    FastAPI,
    Request,
    Form,
    Depends
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
)

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from starlette.middleware.sessions import SessionMiddleware

from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy import func

from passlib.context import CryptContext

from backend.database import (
    Base,
    engine,
    get_db
)

from backend.models import (
    Admin,
    Member,
    Payment,
    Expense
)

# =====================================================
# DATABASE
# =====================================================

Base.metadata.create_all(bind=engine)

# =====================================================
# PASSWORD HASHING
# =====================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# =====================================================
# FASTAPI APP
# =====================================================

app = FastAPI(

    title="KN STREET CHA RAJA",

    version="3.0"

)
print("=" * 60)
print("RUNNING APP.PY FROM:", __file__)
print("=" * 60)

# =====================================================
# SESSION
# =====================================================

app.add_middleware(

    SessionMiddleware,

    secret_key="knstreetcharaja-secret-key"

)

# =====================================================
# STATIC FILES
# =====================================================

app.mount(

    "/static",

    StaticFiles(directory="static"),

    name="static"

)

# =====================================================
# TEMPLATES
# =====================================================

templates = Jinja2Templates(

    directory="templates"

)

# =====================================================
# LOGIN CHECK
# =====================================================

def check_login(request: Request):

    if not request.session.get("user"):

        return RedirectResponse(

            "/login",

            status_code=302

        )

    return None

# =====================================================
# HOME
# =====================================================

@app.get("/")
async def home():

    return RedirectResponse(

        "/login",

        status_code=302

    )
# =====================================================
# LOGIN PAGE
# =====================================================

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):

    if request.session.get("user"):

        return RedirectResponse(
            "/dashboard",
            status_code=302
        )

    return templates.TemplateResponse(

        "login.html",

        {

            "request": request,

            "error": ""

        }

    )
# =====================================================
# LOGOUT
# =====================================================

@app.get("/logout")
async def logout(request: Request):

    request.session.clear()

    return RedirectResponse(
        "/login",
        status_code=302
    )


# =====================================================
# CREATE ADMIN (RUN ONLY ONCE)
# http://127.0.0.1:8000/create-admin
# =====================================================

@app.get("/create-admin")
async def create_admin(

    db: Session = Depends(get_db)

):

    admin = db.query(Admin).filter(

        Admin.username == "admin"

    ).first()

    if admin:

        return {

            "message": "Admin already exists"

        }

    admin = Admin(

        username="admin",

        password=pwd_context.hash("admin123")

    )

    db.add(admin)

    db.commit()

    db.refresh(admin)

    return {

        "message": "Admin created successfully",

        "username": "admin",

        "password": "admin123"

    }


# =====================================================
# LOGIN
# =====================================================

@app.post("/login")
async def login(

    request: Request,

    username: str = Form(...),

    password: str = Form(...),

    db: Session = Depends(get_db)

):

    admin = db.query(Admin).filter(

        Admin.username == username

    ).first()

    if not admin:

        return templates.TemplateResponse(

            "login.html",

            {

                "request": request,

                "error": "Invalid Username or Password"

            }

        )

    if not pwd_context.verify(

        password,

        admin.password

    ):

        return templates.TemplateResponse(

            "login.html",

            {

                "request": request,

                "error": "Invalid Username or Password"

            }

        )

    request.session["user"] = admin.username

    return RedirectResponse(

        url="/dashboard",

        status_code=302

    )


# =====================================================
# LOGOUT
# =====================================================

@app.get("/logout")
async def logout(request: Request):

    request.session.clear()

    return RedirectResponse(

        "/login",

        status_code=302

    )
# =====================================================
# DASHBOARD
# =====================================================

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):

    auth = check_login(request)

    if auth:
        return auth


    # ================= MEMBERS =================


    members = db.query(Member).all()


    total_members = len(members)


    paid_members = len(
        [m for m in members if m.status == "Paid"]
    )


    partial_members = len(
        [m for m in members if m.status == "Partial"]
    )


    pending_members = len(
        [m for m in members if m.status == "Pending"]
    )



    # ================= PAYMENTS =================


    payments = db.query(Payment).all()



    total_collection = sum(
        p.amount or 0
        for p in payments
    )


    cash_collection = sum(
        p.amount or 0
        for p in payments
        if p.payment_mode == "Cash"
    )


    upi_collection = sum(
        p.amount or 0
        for p in payments
        if p.payment_mode == "UPI"
    )


    bank_collection = sum(
        p.amount or 0
        for p in payments
        if p.payment_mode == "Bank"
    )



    # ================= EXPENSES =================


    expenses = db.query(Expense).all()



    total_expense = sum(
        e.amount or 0
        for e in expenses
    )


    cash_expense = sum(
        e.amount or 0
        for e in expenses
        if e.payment_mode == "Cash"
    )


    upi_expense = sum(
        e.amount or 0
        for e in expenses
        if e.payment_mode == "UPI"
    )


    bank_expense = sum(
        e.amount or 0
        for e in expenses
        if e.payment_mode == "Bank"
    )



    # ================= BALANCE =================


    balance = total_collection - total_expense


    cash_balance = cash_collection - cash_expense


    upi_balance = upi_collection - upi_expense


    bank_balance = bank_collection - bank_expense



    # ================= EXPECTED =================


    expected_collection = sum(
        m.expected_amount or 0
        for m in members
    )


    pending_amount = max(
        expected_collection - total_collection,
        0
    )


    progress_percent = 0


    if expected_collection:

        progress_percent = round(
            (total_collection / expected_collection) * 100
        )



    # ================= TODAY =================


    today = date.today()


    today_collection = sum(
        p.amount or 0
        for p in payments
        if str(p.payment_date) == str(today)
    )


    today_expense = sum(
        e.amount or 0
        for e in expenses
        if str(e.expense_date) == str(today)
    )


    today_balance = today_collection - today_expense




    # ================= INVENTORY =================


    total_rice_packets = (

        db.query(Payment)

        .filter(
            Payment.contribution_type == "Rice Packet"
        )

        .with_entities(
            func.sum(Payment.quantity)
        )

        .scalar()

        or 0

    )



    total_laddus = (

        db.query(Payment)

        .filter(
            Payment.contribution_type == "Laddu"
        )

        .with_entities(
            func.sum(Payment.quantity)
        )

        .scalar()

        or 0

    )




    # ================= RECENT =================


    recent_payments = (

        db.query(Payment)

        .order_by(
            Payment.id.desc()
        )

        .limit(5)

        .all()

    )



    recent_expenses = (

        db.query(Expense)

        .order_by(
            Expense.id.desc()
        )

        .limit(5)

        .all()

    )





    # ================= RENDER =================


    return templates.TemplateResponse(

        "dashboard.html",

        {

            "request": request,


            "total_members": total_members,

            "paid_members": paid_members,

            "partial_members": partial_members,

            "pending_members": pending_members,


            "total_collection": total_collection,

            "cash_collection": cash_collection,

            "upi_collection": upi_collection,

            "bank_collection": bank_collection,


            "total_expense": total_expense,

            "cash_expense": cash_expense,

            "upi_expense": upi_expense,

            "bank_expense": bank_expense,


            "balance": balance,

            "cash_balance": cash_balance,

            "upi_balance": upi_balance,

            "bank_balance": bank_balance,


            "expected_collection": expected_collection,

            "pending_amount": pending_amount,

            "progress_percent": progress_percent,


            "today_collection": today_collection,

            "today_expense": today_expense,

            "today_balance": today_balance,


            "total_rice_packets": total_rice_packets,

            "total_laddus": total_laddus,


            "recent_payments": recent_payments,

            "recent_expenses": recent_expenses

        }

    )
# =====================================================
# MEMBERS
# =====================================================

@app.get("/members", response_class=HTMLResponse)
async def members_page(

    request: Request,

    search: str = "",

    db: Session = Depends(get_db)

):

    auth = check_login(request)

    if auth:
        return auth

    query = db.query(Member)

    if search:

        query = query.filter(

            or_(

                Member.name.ilike(f"%{search}%"),

                Member.mobile.ilike(f"%{search}%"),

                Member.house_no.ilike(f"%{search}%"),

                Member.area.ilike(f"%{search}%")

            )

        )

    members = query.order_by(

        Member.id.desc()

    ).all()

    total_members = len(members)

    paid_members = len(

        [m for m in members if m.status == "Paid"]

    )

    partial_members = len(

        [m for m in members if m.status == "Partial"]

    )

    pending_members = len(

        [m for m in members if m.status == "Pending"]

    )

    total_expected = sum(

        m.expected_amount or 0

        for m in members

    )

    total_paid = sum(

        m.paid_amount or 0

        for m in members

    )

    pending_amount = max(

        total_expected - total_paid,

        0

    )

    return templates.TemplateResponse(

        "members.html",

        {

            "request": request,

            "members": members,

            "search": search,

            "total_members": total_members,

            "paid_members": paid_members,

            "partial_members": partial_members,

            "pending_members": pending_members,

            "total_expected": total_expected,

            "total_paid": total_paid,

            "pending_amount": pending_amount

        }

    )

# =====================================================
# PAYMENT PAGE FOR MEMBER
# =====================================================

@app.get("/payment/{member_id}", response_class=HTMLResponse)
async def payment_member(
    request: Request,
    member_id: int,
    db: Session = Depends(get_db)
):

    auth = check_login(request)
    if auth:
        return auth

    member = (
        db.query(Member)
        .filter(Member.id == member_id)
        .first()
    )

    if not member:
        return RedirectResponse("/members", status_code=302)

    members = db.query(Member).order_by(Member.name).all()

    payments = (
        db.query(Payment)
        .order_by(Payment.id.desc())
        .all()
    )

    total_collection = sum(p.amount or 0 for p in payments)

    cash_collection = sum(
        p.amount or 0
        for p in payments
        if p.payment_mode == "Cash"
    )

    upi_collection = sum(
        p.amount or 0
        for p in payments
        if p.payment_mode == "UPI"
    )

    bank_collection = sum(
        p.amount or 0
        for p in payments
        if p.payment_mode == "Bank"
    )

    return templates.TemplateResponse(
        "payment.html",
        {
            "request": request,
            "member": member,
            "members": members,
            "payments": payments,
            "total_collection": total_collection,
            "cash_collection": cash_collection,
            "upi_collection": upi_collection,
            "bank_collection": bank_collection
        }
    )

# =====================================================
# ADD MEMBER PAGE
# =====================================================

@app.get("/add-member", response_class=HTMLResponse)
async def add_member_page(

    request: Request

):

    auth = check_login(request)

    if auth:
        return auth

    return templates.TemplateResponse(

        "add_member.html",

        {

            "request": request

        }

    )


# =====================================================
# SAVE MEMBER
# =====================================================

@app.post("/save-member")
async def save_member(

    request: Request,

    name: str = Form(...),

    mobile: str = Form(...),

    house_no: str = Form(""),

    area: str = Form(""),

    address: str = Form(""),

    expected_amount: int = Form(500),

    paid_amount: int = Form(0),

    payment_mode: str = Form(""),

    payment_date: str = Form(""),

    collected_by: str = Form(""),

    remarks: str = Form(""),

    db: Session = Depends(get_db)

):

    auth = check_login(request)

    if auth:
        return auth

    if paid_amount >= expected_amount:

        status = "Paid"

    elif paid_amount > 0:

        status = "Partial"

    else:

        status = "Pending"

    member = Member(

        name=name,

        mobile=mobile,

        house_no=house_no,

        area=area,

        address=address,

        expected_amount=expected_amount,

        paid_amount=paid_amount,

        payment_mode=payment_mode,

        payment_date=payment_date,

        collected_by=collected_by,

        remarks=remarks,

        status=status

    )

    db.add(member)

    db.commit()

    db.refresh(member)

    return RedirectResponse(

        "/members",

        status_code=302

    )
# =====================================================
# EDIT MEMBER
# =====================================================

@app.get("/edit-member/{member_id}", response_class=HTMLResponse)
async def edit_member(

    request: Request,

    member_id: int,

    db: Session = Depends(get_db)

):

    auth = check_login(request)

    if auth:
        return auth

    member = db.query(Member).filter(

        Member.id == member_id

    ).first()

    if not member:

        return RedirectResponse(

            "/members",

            status_code=302

        )

    return templates.TemplateResponse(

        "edit_member.html",

        {

            "request": request,

            "member": member

        }

    )
# =====================================================
# DELETE MEMBER
# =====================================================

@app.get("/delete-member/{member_id}")
async def delete_member(

    member_id: int,

    db: Session = Depends(get_db)

):

    member = db.query(Member).filter(

        Member.id == member_id

    ).first()

    if member:

        db.delete(member)

        db.commit()

    return RedirectResponse(

        "/members",

        status_code=302

    )
# =====================================================
# PAYMENTS
# =====================================================

@app.get("/payments", response_class=HTMLResponse)
async def payments_page(
    request: Request,
    db: Session = Depends(get_db)
):

    auth = check_login(request)
    if auth:
        return auth

    members = (
        db.query(Member)
        .order_by(Member.name)
        .all()
    )

    payments = (
        db.query(Payment)
        .order_by(Payment.id.desc())
        .all()
    )

    total_collection = sum(p.amount or 0 for p in payments)

    cash_collection = sum(
        p.amount or 0
        for p in payments
        if p.payment_mode == "Cash"
    )

    upi_collection = sum(
        p.amount or 0
        for p in payments
        if p.payment_mode == "UPI"
    )

    bank_collection = sum(
        p.amount or 0
        for p in payments
        if p.payment_mode == "Bank"
    )

    return templates.TemplateResponse(

        "payment.html",

        {

            "request": request,

            "members": members,

            "payments": payments,

            "total_collection": total_collection,

            "cash_collection": cash_collection,

            "upi_collection": upi_collection,

            "bank_collection": bank_collection

        }

    )

# =====================================================
# SAVE PAYMENT
# =====================================================

@app.post("/save-payment")
async def save_payment(

    member_id: int = Form(...),

    contribution_type: str = Form("Chanda"),

    quantity: int = Form(0),

    sponsor_details: str = Form(""),

    amount: int = Form(0),

    payment_mode: str = Form("Cash"),

    payment_date: str = Form(...),

    next_payment_date: str = Form(""),

    received_by: str = Form(""),

    transaction_id: str = Form(""),

    remarks: str = Form(""),

    db: Session = Depends(get_db)

):


    member = (

        db.query(Member)

        .filter(
            Member.id == member_id
        )

        .first()

    )


    if not member:

        return RedirectResponse(

            "/payments",

            status_code=302

        )



    # ================= CREATE PAYMENT =================


    payment = Payment(

        member_id = member.id,

        contribution_type = contribution_type,

        quantity = quantity,

        sponsor_details = sponsor_details,

        amount = amount,

        payment_mode = payment_mode,

        payment_date = payment_date,

        next_payment_date = next_payment_date,

        received_by = received_by,

        transaction_id = transaction_id,

        remarks = remarks

    )


    db.add(payment)



    # ================= UPDATE MEMBER PAYMENT =================


    # Rice Packet and Laddu are item contributions
    # They should not increase money collection


    if contribution_type not in [

        "Rice Packet",

        "Laddu"

    ]:

        member.paid_amount += amount



    member.payment_mode = payment_mode

    member.payment_date = payment_date

    member.collected_by = received_by



    if member.paid_amount >= member.expected_amount:


        member.status = "Paid"


    elif member.paid_amount > 0:


        member.status = "Partial"


    else:


        member.status = "Pending"



    db.commit()


    db.refresh(payment)



    return RedirectResponse(

        "/payments",

        status_code=302

    )
# =====================================================
# DELETE PAYMENT
# =====================================================

@app.get("/delete-payment/{payment_id}")
async def delete_payment(

    payment_id: int,

    db: Session = Depends(get_db)

):

    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )

    if payment:

        member = (
            db.query(Member)
            .filter(Member.id == payment.member_id)
            .first()
        )

        if member:

            member.paid_amount -= payment.amount

            if member.paid_amount < 0:
                member.paid_amount = 0

            if member.paid_amount >= member.expected_amount:

                member.status = "Paid"

            elif member.paid_amount > 0:

                member.status = "Partial"

            else:

                member.status = "Pending"

        db.delete(payment)

        db.commit()

    return RedirectResponse(

        "/payments",

        status_code=302

    )


# =====================================================
# PAYMENT HISTORY
# =====================================================

@app.get("/payment-history", response_class=HTMLResponse)
async def payment_history(

    request: Request,

    db: Session = Depends(get_db)

):

    auth = check_login(request)

    if auth:
        return auth

    payments = (
        db.query(Payment)
        .order_by(Payment.payment_date.desc())
        .all()
    )

    return templates.TemplateResponse(

        "payment.html",

        {

            "request": request,

            "payments": payments,

            "members": db.query(Member).all()

        }

    )
# =====================================================
# EXPENSES PAGE
# =====================================================

@app.get("/expenses", response_class=HTMLResponse)
async def expenses_page(
    request: Request,
    db: Session = Depends(get_db)
):

    auth = check_login(request)
    if auth:
        return auth

    expenses = (
        db.query(Expense)
        .order_by(Expense.id.desc())
        .all()
    )

    total_expense = sum(
        e.amount or 0
        for e in expenses
    )

    cash_expense = sum(
        e.amount or 0
        for e in expenses
        if e.payment_mode == "Cash"
    )

    upi_expense = sum(
        e.amount or 0
        for e in expenses
        if e.payment_mode == "UPI"
    )

    bank_expense = sum(
        e.amount or 0
        for e in expenses
        if e.payment_mode == "Bank"
    )

    return templates.TemplateResponse(

        "expenses.html",

        {

            "request": request,

            "expenses": expenses,

            "total_expense": total_expense,

            "cash_expense": cash_expense,

            "upi_expense": upi_expense,

            "bank_expense": bank_expense

        }

    )
# =====================================================
# SAVE EXPENSE
# =====================================================

@app.post("/save-expense")
async def save_expense(

    expense_type: str = Form(...),

    category: str = Form(...),

    amount: int = Form(...),

    payment_mode: str = Form(...),

    paid_by: str = Form(...),

    expense_date: str = Form(...),

    transaction_id: str = Form(""),

    remarks: str = Form(""),

    db: Session = Depends(get_db)

):

    expense = Expense(

        expense_type=expense_type,

        category=category,

        amount=amount,

        payment_mode=payment_mode,

        paid_by=paid_by,

        expense_date=expense_date,

        transaction_id=transaction_id,

        remarks=remarks

    )

    db.add(expense)

    db.commit()

    db.refresh(expense)

    return RedirectResponse(

        "/expenses",

        status_code=302

    )
# =====================================================
# EDIT EXPENSE
# =====================================================

@app.get("/edit-expense/{expense_id}", response_class=HTMLResponse)
async def edit_expense(

    request: Request,

    expense_id: int,

    db: Session = Depends(get_db)

):

    auth = check_login(request)

    if auth:
        return auth

    expense = (
        db.query(Expense)
        .filter(Expense.id == expense_id)
        .first()
    )

    if not expense:

        return RedirectResponse(
            "/expenses",
            status_code=302
        )

    return templates.TemplateResponse(

        "expenses.html",

        {

            "request": request,

            "expense": expense

        }

    )
# =====================================================
# UPDATE EXPENSE
# =====================================================

@app.post("/update-expense/{expense_id}")
async def update_expense(

    expense_id: int,

    expense_type: str = Form(...),

    category: str = Form(...),

    amount: int = Form(...),

    payment_mode: str = Form(...),

    paid_by: str = Form(...),

    expense_date: str = Form(...),

    transaction_id: str = Form(""),

    remarks: str = Form(""),

    db: Session = Depends(get_db)

):

    expense = (
        db.query(Expense)
        .filter(Expense.id == expense_id)
        .first()
    )

    if not expense:

        return RedirectResponse(
            "/expenses",
            status_code=302
        )

    expense.expense_type = expense_type
    expense.category = category
    expense.amount = amount
    expense.payment_mode = payment_mode
    expense.paid_by = paid_by
    expense.expense_date = expense_date
    expense.transaction_id = transaction_id
    expense.remarks = remarks

    db.commit()

    return RedirectResponse(

        "/expenses",

        status_code=302

    )
# =====================================================
# DELETE EXPENSE
# =====================================================

@app.get("/delete-expense/{expense_id}")
async def delete_expense(

    expense_id: int,

    db: Session = Depends(get_db)

):

    expense = (
        db.query(Expense)
        .filter(Expense.id == expense_id)
        .first()
    )

    if expense:

        db.delete(expense)

        db.commit()

    return RedirectResponse(

        "/expenses",

        status_code=302

    )
# =====================================================
# ANALYTICS
# =====================================================

@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(
    request: Request,
    db: Session = Depends(get_db)
):

    auth = check_login(request)
    if auth:
        return auth

    members = db.query(Member).all()
    payments = db.query(Payment).all()
    expenses = db.query(Expense).all()

    total_members = len(members)

    paid_members = len(
        [m for m in members if m.status == "Paid"]
    )

    partial_members = len(
        [m for m in members if m.status == "Partial"]
    )

    pending_members = len(
        [m for m in members if m.status == "Pending"]
    )

    total_collection = sum(
        p.amount or 0
        for p in payments
    )

    total_expense = sum(
        e.amount or 0
        for e in expenses
    )

    balance = total_collection - total_expense

    return templates.TemplateResponse(

        "analytics.html",

        {

            "request": request,

            "total_members": total_members,

            "paid_members": paid_members,

            "partial_members": partial_members,

            "pending_members": pending_members,

            "total_collection": total_collection,

            "total_expense": total_expense,

            "balance": balance,

            "payments": payments,

            "expenses": expenses

        }

    )
# =====================================================
# CHANGE PASSWORD
# =====================================================

@app.get("/change-password", response_class=HTMLResponse)
async def change_password_page(

    request: Request

):

    auth = check_login(request)

    if auth:
        return auth

    return templates.TemplateResponse(

        "change_password.html",

        {

            "request": request,

            "message": ""

        }

    )


@app.post("/change-password")
async def change_password(

    request: Request,

    current_password: str = Form(...),

    new_password: str = Form(...),

    confirm_password: str = Form(...),

    db: Session = Depends(get_db)

):

    auth = check_login(request)

    if auth:
        return auth

    admin = db.query(Admin).filter(

        Admin.username == request.session["user"]

    ).first()

    if not pwd_context.verify(

        current_password,

        admin.password

    ):

        return templates.TemplateResponse(

            "change_password.html",

            {

                "request": request,

                "message": "Current password is incorrect."

            }

        )

    if new_password != confirm_password:

        return templates.TemplateResponse(

            "change_password.html",

            {

                "request": request,

                "message": "Passwords do not match."

            }

        )

    admin.password = pwd_context.hash(

        new_password

    )

    db.commit()

    return templates.TemplateResponse(

        "change_password.html",

        {

            "request": request,

            "message": "Password updated successfully."

        }

    )
# =====================================================
# SYSTEM STATUS
# =====================================================

@app.get("/health")
async def health():

    return {

        "status": "running",

        "application": "KN STREET CHA RAJA",

        "version": "3.0"

    }