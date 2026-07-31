from starlette.middleware.sessions import SessionMiddleware

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from sqlalchemy import or_

from passlib.context import CryptContext

from backend.database import engine, Base, get_db
from backend.models import Member, Payment, Expense, Admin

# =====================================================
# CREATE DATABASE
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
    title="MandalFlow",
    version="2.0"
)

# =====================================================
# SESSION
# =====================================================

app.add_middleware(
    SessionMiddleware,
    secret_key="mandalflow-secret-key-change-this"
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

templates = Jinja2Templates(directory="templates")

# =====================================================
# HOME
# =====================================================

@app.get("/")
async def home():
    return RedirectResponse("/login", status_code=302)

# =====================================================
# LOGIN PAGE
# =====================================================

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):

    if request.session.get("user"):
        return RedirectResponse("/dashboard", status_code=302)

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": ""
        }
    )

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

    if admin and pwd_context.verify(password, admin.password):
        request.session["user"] = admin.username
        return RedirectResponse(
            "/dashboard",
            status_code=302
        )

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": "Invalid Username or Password"
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
# CREATE FIRST ADMIN
# Run only once:
# http://127.0.0.1:8000/create-admin
# =====================================================

@app.get("/create-admin")
async def create_admin(
    db: Session = Depends(get_db)
):

    existing = db.query(Admin).filter(
        Admin.username == "admin"
    ).first()

    if existing:
        return {
            "message": "Admin already exists"
        }

    admin = Admin(
        username="admin",
        password=pwd_context.hash("admin123")
    )

    db.add(admin)
    db.commit()

    return {
        "message": "Admin Created Successfully"
    }

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

    total_members = db.query(Member).count()

    total_collection = sum(
        payment.amount or 0
        for payment in db.query(Payment).all()
    )

    total_expense = sum(
        expense.amount or 0
        for expense in db.query(Expense).all()
    )

    pending_members = db.query(Member).filter(
        Member.status == "Pending"
    ).count()

    return templates.TemplateResponse(
    "index.html",
        {
            "request": request,
            "total_members": total_members,
            "total_collection": total_collection,
            "total_expense": total_expense,
            "balance": total_collection - total_expense,
            "pending_members": pending_members
        }
    )

# =====================================================
# MEMBERS
# =====================================================

@app.get("/members", response_class=HTMLResponse)
async def members(
    request: Request,
    search: str = "",
    db: Session = Depends(get_db)
):

    auth = check_login(request)
    if auth:
        return auth

    if search:

        members = db.query(Member).filter(
            or_(
                Member.name.ilike(f"%{search}%"),
                Member.mobile.ilike(f"%{search}%"),
                Member.area.ilike(f"%{search}%"),
                Member.house_no.ilike(f"%{search}%")
            )
        ).all()

    else:

        members = db.query(Member).order_by(
            Member.id.desc()
        ).all()

    return templates.TemplateResponse(
        "members.html",
        {
            "request": request,
            "members": members,
            "search": search
        }
    )

# =====================================================
# ADD MEMBER PAGE
# =====================================================

@app.get("/add-member", response_class=HTMLResponse)
async def add_member(request: Request):

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

    status = "Paid"

    if paid_amount < expected_amount:
        status = "Pending"

    member = Member(

        name=name,
        mobile=mobile,

        house_no=house_no,
        area=area,
        address=address,

        expected_amount=expected_amount,
        paid_amount=paid_amount,

        status=status,

        payment_mode=payment_mode,
        payment_date=payment_date,

        collected_by=collected_by,

        remarks=remarks
    )

    db.add(member)
    db.commit()

    return RedirectResponse(
        "/members",
        status_code=302
    )
# =====================================================
# EDIT MEMBER
# =====================================================

@app.get("/edit-member/{member_id}", response_class=HTMLResponse)
async def edit_member(
    member_id: int,
    request: Request,
    db: Session = Depends(get_db)
):

    auth = check_login(request)
    if auth:
        return auth

    member = db.query(Member).filter(
        Member.id == member_id
    ).first()

    if not member:
        return HTMLResponse(
            "<h2>Member Not Found</h2>",
            status_code=404
        )

    return templates.TemplateResponse(
        "edit_member.html",
        {
            "request": request,
            "member": member
        }
    )


# =====================================================
# UPDATE MEMBER
# =====================================================

@app.post("/update-member")
async def update_member(

    request: Request,

    member_id: int = Form(...),

    name: str = Form(...),
    mobile: str = Form(...),

    house_no: str = Form(""),
    area: str = Form(""),
    address: str = Form(""),

    expected_amount: int = Form(...),

    db: Session = Depends(get_db)

):

    auth = check_login(request)
    if auth:
        return auth

    member = db.query(Member).filter(
        Member.id == member_id
    ).first()

    if member:

        member.name = name
        member.mobile = mobile
        member.house_no = house_no
        member.area = area
        member.address = address
        member.expected_amount = expected_amount

        if member.paid_amount >= member.expected_amount:
            member.status = "Paid"

        elif member.paid_amount > 0:
            member.status = "Partial"

        else:
            member.status = "Pending"

        db.commit()

    return RedirectResponse(
        "/members",
        status_code=302
    )


# =====================================================
# DELETE MEMBER
# =====================================================

@app.get("/delete-member/{member_id}")
async def delete_member(
    member_id: int,
    request: Request,
    db: Session = Depends(get_db)
):

    auth = check_login(request)
    if auth:
        return auth

    db.query(Payment).filter(
        Payment.member_id == member_id
    ).delete()

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
# MEMBER DETAILS
# =====================================================

@app.get("/member/{member_id}", response_class=HTMLResponse)
async def member_details(
    member_id: int,
    request: Request,
    db: Session = Depends(get_db)
):

    auth = check_login(request)
    if auth:
        return auth

    member = db.query(Member).filter(
        Member.id == member_id
    ).first()

    if not member:
        return HTMLResponse(
            "<h2>Member Not Found</h2>",
            status_code=404
        )

    payments = db.query(Payment).filter(
        Payment.member_id == member_id
    ).order_by(
        Payment.id.desc()
    ).all()

    return templates.TemplateResponse(
        "member.html",
        {
            "request": request,
            "member": member,
            "payments": payments
        }
    )
# =====================================================
# PAYMENT PAGE
# =====================================================

@app.get("/payment/{member_id}", response_class=HTMLResponse)
async def payment_page(
    member_id: int,
    request: Request,
    db: Session = Depends(get_db)
):

    auth = check_login(request)
    if auth:
        return auth

    member = db.query(Member).filter(
        Member.id == member_id
    ).first()

    if not member:
        return HTMLResponse(
            "<h2>Member Not Found</h2>",
            status_code=404
        )

    return templates.TemplateResponse(
        "payment.html",
        {
            "request": request,
            "member": member
        }
    )


# =====================================================
# SAVE PAYMENT
# =====================================================

@app.post("/save-payment")
async def save_payment(

    request: Request,

    member_id: int = Form(...),
    contribution_type: str = Form(...),
    amount: int = Form(...),
    payment_mode: str = Form(...),
    payment_date: str = Form(...),
    next_payment_date: str = Form(""),
    remarks: str = Form(""),

    db: Session = Depends(get_db)

):

    auth = check_login(request)
    if auth:
        return auth

    payment = Payment(

        member_id=member_id,
        contribution_type=contribution_type,
        amount=amount,
        payment_mode=payment_mode,
        payment_date=payment_date,
        next_payment_date=next_payment_date,
        received_by=request.session.get("user"),
        remarks=remarks

    )

    db.add(payment)

    member = db.query(Member).filter(
        Member.id == member_id
    ).first()

    if member:

        member.paid_amount += amount

        if member.paid_amount >= member.expected_amount:
            member.status = "Paid"

        elif member.paid_amount > 0:
            member.status = "Partial"

        else:
            member.status = "Pending"

        member.payment_mode = payment_mode
        member.payment_date = payment_date
        member.collected_by = request.session.get("user")

    db.commit()

    return RedirectResponse(
        url=f"/member/{member_id}",
        status_code=302
    )
# =====================================================
# EXPENSES PAGE
# =====================================================

@app.get("/expenses", response_class=HTMLResponse)
async def expenses(
    request: Request,
    db: Session = Depends(get_db)
):

    auth = check_login(request)
    if auth:
        return auth

    expenses = db.query(Expense).order_by(
        Expense.id.desc()
    ).all()

    total_expenses = sum(
        expense.amount
        for expense in expenses
    )

    return templates.TemplateResponse(
        "expenses.html",
        {
            "request": request,
            "expenses": expenses,
            "total_expenses": total_expenses
        }
    )


# =====================================================
# SAVE EXPENSE
# =====================================================

@app.post("/save-expense")
async def save_expense(

    request: Request,

    expense_type: str = Form(...),
    amount: int = Form(...),
    payment_mode: str = Form(...),
    paid_by: str = Form(...),
    expense_date: str = Form(...),
    remarks: str = Form(""),

    db: Session = Depends(get_db)

):

    auth = check_login(request)
    if auth:
        return auth

    expense = Expense(
        expense_type=expense_type,
        amount=amount,
        payment_mode=payment_mode,
        paid_by=paid_by,
        expense_date=expense_date,
        remarks=remarks
    )

    db.add(expense)
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
    request: Request,
    db: Session = Depends(get_db)
):

    auth = check_login(request)
    if auth:
        return auth

    expense = db.query(Expense).filter(
        Expense.id == expense_id
    ).first()

    if expense:
        db.delete(expense)
        db.commit()

    return RedirectResponse(
        "/expenses",
        status_code=302
    )


# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/health")
async def health():

    return {
        "status": "running",
        "application": "MandalFlow",
        "version": "2.0"
    }