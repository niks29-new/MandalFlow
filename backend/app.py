from starlette.middleware.sessions import SessionMiddleware

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.database import engine, Base, get_db
from backend.models import Member, Payment, Expense

# =====================================================
# CREATE DATABASE
# =====================================================

Base.metadata.create_all(bind=engine)

# =====================================================
# FASTAPI APP
# =====================================================

app = FastAPI(
    title="MandalFlow",
    version="1.0"
)

# =====================================================
# SESSION MIDDLEWARE
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
    password: str = Form(...)
):

    if username == "admin" and password == "admin123":

        request.session["user"] = username

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
# DASHBOARD
# =====================================================

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):

    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=302)

    members = db.query(Member).all()
    payments = db.query(Payment).all()
    expenses = db.query(Expense).all()

    total_members = len(members)

    total_collection = sum(p.amount for p in payments)
    total_expenses = sum(e.amount for e in expenses)

    available_balance = total_collection - total_expenses

    total_expected = sum(m.expected_amount for m in members)
    pending_amount = total_expected - total_collection

    paid_members = len(
        [m for m in members if m.status == "Paid"]
    )

    partial_members = len(
        [m for m in members if m.status == "Partial"]
    )

    pending_members = len(
        [m for m in members if m.status == "Pending"]
    )

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "total_members": total_members,
            "total_collection": total_collection,
            "total_expenses": total_expenses,
            "available_balance": available_balance,
            "pending_amount": pending_amount,
            "paid_members": paid_members,
            "partial_members": partial_members,
            "pending_members": pending_members,
        }
    )
# =====================================================
# MEMBERS LIST
# =====================================================

@app.get("/members", response_class=HTMLResponse)
async def members(
    request: Request,
    search: str = "",
    db: Session = Depends(get_db)
):

    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=302)

    query = db.query(Member)

    if search:
        query = query.filter(
            or_(
                Member.name.ilike(f"%{search}%"),
                Member.mobile.ilike(f"%{search}%"),
                Member.area.ilike(f"%{search}%")
            )
        )

    members = query.order_by(Member.id.desc()).all()

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

    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=302)

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
    house_no: str = Form(...),
    area: str = Form(...),
    expected_amount: int = Form(...),

    db: Session = Depends(get_db)

):

    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=302)

    member = Member(
        name=name,
        mobile=mobile,
        house_no=house_no,
        area=area,
        expected_amount=expected_amount,
        paid_amount=0,
        status="Pending"
    )

    db.add(member)
    db.commit()

    return RedirectResponse(
        url="/members",
        status_code=303
    )


# =====================================================
# EDIT MEMBER PAGE
# =====================================================

@app.get("/edit-member/{member_id}", response_class=HTMLResponse)
async def edit_member(
    member_id: int,
    request: Request,
    db: Session = Depends(get_db)
):

    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=302)

    member = db.query(Member).filter(
        Member.id == member_id
    ).first()

    if member is None:
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
    house_no: str = Form(...),
    area: str = Form(...),
    expected_amount: int = Form(...),

    db: Session = Depends(get_db)

):

    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=302)

    member = db.query(Member).filter(
        Member.id == member_id
    ).first()

    if member:

        member.name = name
        member.mobile = mobile
        member.house_no = house_no
        member.area = area
        member.expected_amount = expected_amount

        db.commit()

    return RedirectResponse(
        url="/members",
        status_code=303
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

    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=302)

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
        url="/members",
        status_code=303
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

    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=302)

    member = db.query(Member).filter(
        Member.id == member_id
    ).first()

    if member is None:
        return HTMLResponse(
            "<h2>Member Not Found</h2>",
            status_code=404
        )

    payments = (
        db.query(Payment)
        .filter(Payment.member_id == member_id)
        .order_by(Payment.id.desc())
        .all()
    )

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

    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=302)

    member = db.query(Member).filter(
        Member.id == member_id
    ).first()

    if member is None:
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
    payment_date: str = Form(""),
    next_payment_date: str = Form(""),
    remarks: str = Form(""),

    db: Session = Depends(get_db)

):

    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=302)

    payment = Payment(
        member_id=member_id,
        contribution_type=contribution_type,
        amount=amount,
        payment_mode=payment_mode,
        payment_date=payment_date,
        next_payment_date=next_payment_date,
        received_by="Admin",
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

    db.commit()

    return RedirectResponse(
        url=f"/member/{member_id}",
        status_code=303
    )
# =====================================================
# EXPENSES LIST
# =====================================================

@app.get("/expenses", response_class=HTMLResponse)
async def expenses(
    request: Request,
    db: Session = Depends(get_db)
):

    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=302)

    expenses = db.query(Expense).order_by(Expense.id.desc()).all()

    total_expenses = sum(exp.amount for exp in expenses)

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

    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=302)

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
        url="/expenses",
        status_code=303
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

    if not request.session.get("user"):
        return RedirectResponse("/login", status_code=302)

    expense = db.query(Expense).filter(
        Expense.id == expense_id
    ).first()

    if expense:
        db.delete(expense)
        db.commit()

    return RedirectResponse(
        url="/expenses",
        status_code=303
    )


# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/health")
async def health():

    return {
        "status": "running",
        "application": "MandalFlow"
    }