from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from backend.database import engine, Base, get_db
from backend.models import Member

# Create Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MandalFlow",
    version="1.0"
)

# Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")


# ==========================================
# HOME
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


# ==========================================
# DASHBOARD
# ==========================================

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


# ==========================================
# MEMBERS LIST
# ==========================================

@app.get("/members", response_class=HTMLResponse)
async def members(
    request: Request,
    db: Session = Depends(get_db)
):

    members = db.query(Member).all()

    return templates.TemplateResponse(
        "members.html",
        {
            "request": request,
            "members": members
        }
    )


# ==========================================
# ADD MEMBER PAGE
# ==========================================

@app.get("/add-member", response_class=HTMLResponse)
async def add_member(request: Request):

    return templates.TemplateResponse(
        "add_member.html",
        {
            "request": request
        }
    )


# ==========================================
# SAVE MEMBER
# ==========================================

@app.post("/save-member")
async def save_member(

    name: str = Form(...),
    mobile: str = Form(...),
    house_no: str = Form(...),
    area: str = Form(...),
    expected_amount: int = Form(...),

    db: Session = Depends(get_db)

):

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


# ==========================================
# MEMBER DETAILS
# ==========================================

@app.get("/member/{member_id}", response_class=HTMLResponse)
async def member_details(
    member_id: int,
    request: Request,
    db: Session = Depends(get_db)
):

    member = db.query(Member).filter(Member.id == member_id).first()

    if member is None:
        return HTMLResponse(
            "<h2>Member Not Found</h2>",
            status_code=404
        )

    return templates.TemplateResponse(
        "member.html",
        {
            "request": request,
            "member": member
        }
    )


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/health")
def health():

    return {
        "status": "running",
        "application": "MandalFlow"
    }

# ==========================================
# PAYMENT PAGE
# ==========================================

@app.get("/payment/{member_id}", response_class=HTMLResponse)
async def payment_page(
    member_id: int,
    request: Request,
    db: Session = Depends(get_db)
):

    member = db.query(Member).filter(Member.id == member_id).first()

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