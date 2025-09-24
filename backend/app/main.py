### `backend/app/main.py`
from datetime import datetime
import io
import os
from fastapi import FastAPI, Depends, HTTPException, status, Form,File,UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.orm import selectinload
from backend.app.models import Expense, Membership, Split, User
from .db import engine, Base, get_session
from .config import settings
from .schemas import ExpenseSplitIn, ExpenseSplitOut, ExpenseUpdate, GroupUpdate, SettlementOut, UserCreate, UserOut, Token, GroupCreate, GroupOut, ExpenseCreate, ExpenseOut,MembershipUpdate, BalanceItem,MembershipOut,AddMemberPayload, UserUpdate
from .crud import create_user, delete_user, get_groupMembers, get_user_by_email, create_group,delete_group, add_expense, compute_group_balances, get_user_by_id, get_users,get_expenses,get_groups,get_user_by_username,add_member_to_group, update_group, update_user
from .auth import authenticate, create_access_token, get_current_user
from .debt import minimize_cash_flow
 
import pandas as pd
from io import BytesIO




app = FastAPI(title="SplitApp API", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Debug: print tables that SQLAlchemy knows
        print("SQLAlchemy tables:", list(Base.metadata.tables.keys()))  

@app.on_event("shutdown")
async def on_shutdown():
    await engine.dispose()

        

@app.get("/")
async def health():
    return {"status": "ok"}




@app.post("/auth/register", response_model=UserOut)
async def register(user: UserCreate, session: AsyncSession = Depends(get_session)):
    existsUsername = await get_user_by_username(session, user.username)
    if existsUsername:
        raise HTTPException(status_code=400, detail="username already registered")
    existsEmail = await get_user_by_email(session, user.email)
    if existsEmail:
        raise HTTPException(status_code=400, detail="Email already registered")
    u = await create_user(session, email=user.email, username=user.username, password=user.password)
    return UserOut.model_validate(u)


@app.get("/users", response_model=list[UserOut])
async def fetch_users(session: AsyncSession = Depends(get_session), current=Depends(get_current_user)):
    # current is the logged-in user; route is protected
    return await get_users(session)


@app.get("/users/{user_id}", response_model=UserOut)
async def fetch_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current=Depends(get_current_user)
):
    u = await get_user_by_id(session, user_id)
    return  UserOut.model_validate(u)





@app.get("/currentUser", response_model=UserOut)
async def fetch_current_user(current=Depends(get_current_user)):
    return current


@app.get("/users/{user_id}", response_model=UserOut)
async def fetch_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current=Depends(get_current_user)
):
    return await get_user_by_id(session, user_id)


@app.put("/users/{user_id}", response_model=UserOut)
async def edit_user(
    user_id: int,
    payload: UserUpdate,
    session: AsyncSession = Depends(get_session),
    current=Depends(get_current_user)
):
    return await update_user(session, user_id, payload)


@app.delete("/users/{user_id}", status_code=204)
async def remove_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current=Depends(get_current_user)
):
    await delete_user(session, user_id)
    return

@app.post("/auth/login", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    user = await authenticate(session, form.username, form.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(user.username)
    return Token(access_token=token)















# Create group
@app.post("/groups", response_model=GroupOut)
async def create_group_ep(payload: GroupCreate, session: AsyncSession = Depends(get_session), current=Depends(get_current_user)):
    print("befor",current.id)
    group = await create_group(session, name=payload.name, currency=payload.currency, owner_id=current.id, member_ids=payload.member_ids)
    print("after;",current.id)
    return GroupOut.model_validate(group)



# Update group
@app.put("/groups/{group_id}", response_model=GroupOut)
async def route_update_group(group_id: int, payload: GroupUpdate, session: AsyncSession = Depends(get_session), current=Depends(get_current_user)):
    return await update_group(session, group_id, payload.name, payload.currency)

# Delete group
@app.delete("/groups/{group_id}", status_code=204)
async def route_delete_group(group_id: int, session: AsyncSession = Depends(get_session), current=Depends(get_current_user)):
    await delete_group(session, group_id)
    return

# Read all groups
@app.get("/groups", response_model=list[GroupOut])
async def fetch_groups(session: AsyncSession = Depends(get_session), current=Depends(get_current_user)):
    # current is the logged-in user; route is protected
    return await get_groups(session)

@app.get("/groups/{group_id}/members", response_model=list[MembershipOut])
async def get_group_members(
    group_id: int,
    session: AsyncSession = Depends(get_session),
    current=Depends(get_current_user)
):
    return await get_groupMembers(session, group_id)
   




@app.post("/groups/{group_id}/add_member", response_model=MembershipOut)
async def add_member(group_id: int, payload: AddMemberPayload, session: AsyncSession = Depends(get_session)):
    """
    payload should be a Pydantic model:
    class AddMemberPayload(BaseModel):
        user_id: int
        is_admin: bool = False
    """
    membership = await add_member_to_group(session, group_id, payload.user_id, payload.is_admin)
    return membership





"""
@app.get("/groups/{group_id}/members")
async def get_group_members(
    group_id: int,
    session: AsyncSession = Depends(get_session),
    current=Depends(get_current_user)
):
    result = await session.execute(
        select(Membership).where(Membership.group_id == group_id).join(User).where(Membership.user_id == User.id)
    )
    members = result.scalars().all()
    return [MembershipOut.model_validate(m) for m in members]
"""

@app.delete("/groups/{group_id}/members/{member_id}", status_code=204)
async def remove_member(group_id: int, member_id: int, session: AsyncSession = Depends(get_session), current=Depends(get_current_user)):
    result = await session.execute(
        select(Membership).where(Membership.group_id == group_id, Membership.user_id == member_id)
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    await session.delete(membership)
    await session.commit()
    return

@app.put("/groups/{group_id}/members/{member_id}", response_model=MembershipOut)
async def update_member(
    group_id: int, member_id: int, payload: MembershipUpdate,
    session: AsyncSession = Depends(get_session), current=Depends(get_current_user)
):
    result = await session.execute(
        select(Membership).where(Membership.group_id == group_id, Membership.user_id == member_id)
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")

    membership.is_admin = payload.is_admin
    await session.commit()
    await session.refresh(membership)
    return MembershipOut.model_validate(membership)








@app.get("/groups/{group_id}/balances", response_model=list[BalanceItem])
async def group_balances(group_id: int, session: AsyncSession = Depends(get_session), current=Depends(get_current_user)):
    bals = await compute_group_balances(session, group_id)
     # Récupérer usernames des membres
    result = await session.execute(select(User.id, User.username).where(User.id.in_(bals.keys())))
    users = dict(result.all())
    return [BalanceItem(user_id=uid, username=users.get(uid, f"User {uid}"), net=net) for uid, net in sorted(bals.items())]

    
@app.get("/groups/{group_id}/settlements", response_model=list[SettlementOut])
async def group_settlements(group_id: int, session: AsyncSession = Depends(get_session), current=Depends(get_current_user)):
    balances = await compute_group_balances(session, group_id)
    raw_settlements = minimize_cash_flow(balances)  # list of dicts

    # Fetch usernames
    user_ids = {s['from_user'] for s in raw_settlements} | {s['to_user'] for s in raw_settlements}
    result = await session.execute(select(User.id, User.username).where(User.id.in_(user_ids)))
    users = dict(result.all())  # {id: username}

    # Map raw settlements to SettlementOut
    settlements = [
        SettlementOut(
            from_id=s['from_user'],
            from_username=users.get(s['from_user'], f"User {s['from_user']}"),
            to_id=s['to_user'],
            to_username=users.get(s['to_user'], f"User {s['to_user']}"),
            amount=s['amount']
        )
        for s in raw_settlements
    ]

    return settlements








@app.post("/expenses", response_model=ExpenseOut)
async def create_expense_ep(payload: ExpenseCreate,session: AsyncSession = Depends(get_session),current=Depends(get_current_user)):
    splits = [(s.user_id, s.share_amount) for s in payload.splits]
    try:
        # 1️⃣ Create the expense
        exp = await add_expense(session,group_id=payload.group_id,payer_id=current.id,description=payload.description,amount=payload.amount,currency=payload.currency,splits=splits)
        
        # 2️⃣ Load the created expense with its splits eagerly
        result = await session.execute(
            select(Expense)
            .options(selectinload(Expense.splits))
            .where(Expense.id == exp.id)
        )
        exp_with_splits = result.scalar_one()
        
        # 3️⃣ Convert SQLAlchemy Split objects to Pydantic models
        splits_list = [ExpenseSplitIn(user_id=s.user_id, share_amount=s.share_amount)
            for s in exp_with_splits.splits
        ]
        
        # 4️⃣ Return validated Pydantic model
        return ExpenseOut.model_validate(
            ExpenseOut(
                id=exp_with_splits.id,
                group_id=exp_with_splits.group_id,
                payer_id=exp_with_splits.payer_id,
                payer_username=current.username,   # <-- Add this
                description=exp_with_splits.description,
                amount=exp_with_splits.amount,
                currency=exp_with_splits.currency,
                created_at=exp_with_splits.created_at,
                splits=splits_list
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/expense/{expense_id}")
async def delete_expense(expense_id: int, session: AsyncSession = Depends(get_session), current=Depends(get_current_user)):
    expense = await session.get(Expense, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    await session.delete(expense)
    await session.commit()
    return {"message": "Expense deleted successfully"}

@app.put("/expense/{expense_id}")
async def update_expense(
    expense_id: int,
    data: ExpenseUpdate,
    session: AsyncSession = Depends(get_session),
    current=Depends(get_current_user)
):
    expense = await session.get(Expense, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    if data.description is not None:
        expense.description = data.description
    if data.amount is not None:
        expense.amount = data.amount
    if data.category is not None:
        expense.category = data.category
    if data.settled is not None:
        expense.settled = data.settled

    await session.commit()
    await session.refresh(expense)
    return {"message": "Expense updated successfully", "expense": {
        "id": expense.id,
        "description": expense.description,
        "amount": expense.amount,
        "category": expense.category,
        "settled": expense.settled
    }}

@app.get("/expenses/{group_id}", response_model=list[ExpenseOut])
async def get_group_expenses(group_id: int, session: AsyncSession = Depends(get_session)):
    # 1️⃣ Fetch expenses with splits eagerly
    expenses_result = await session.execute(
        select(Expense)
        .where(Expense.group_id == group_id)
        .options(selectinload(Expense.splits).selectinload(Split.user))  # load split.user too
    )
    expenses = expenses_result.scalars().all()

    # 2️⃣ Collect payer_ids
    user_ids = {e.payer_id for e in expenses if e.payer_id is not None}

    # 3️⃣ Fetch usernames for payers
    users_result = await session.execute(select(User.id, User.username).where(User.id.in_(user_ids)))
    users = dict(users_result.all())  # {id: username}

    # 4️⃣ Build response
    result = []
    for e in expenses:
        splits_list = [
            ExpenseSplitOut(
                user_id=s.user_id,
                username=s.user.username if s.user else "Unknown",
                share_amount=s.share_amount
            )
            for s in e.splits
        ]

        result.append(ExpenseOut(
             id=e.id,
             group_id=e.group_id,
             payer_id=e.payer_id,
             payer_username=users.get(e.payer_id, "Unknown"),
             description=e.description,
             amount=e.amount,
             currency=e.currency,
             created_at=e.created_at,
            splits=splits_list
        ))
    return result









 

from .models import Membership, User, Group, Expense, Split

@app.get("/groups/{group_id}/expenses/download-template")
async def download_expenses_template(group_id: int, session: AsyncSession = Depends(get_session)):
    # Get group members
    result = await session.execute(
        select(User)
        .join(Membership)
        .where(Membership.group_id == group_id)
    )
    members = result.scalars().all()  # list of User objects



    # Columns: Name, Paid, Payer,  member1, member2, ...
    columns = ["Name", "Paid", "Payer", ] + [m.username for m in members]
    df = pd.DataFrame(columns=columns)

    # Save to bytes buffer
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f"attachment; filename=group_{group_id}_template.xlsx"})







@app.post("/groups/{group_id}/expenses/upload")
async def upload_expenses(group_id: int, file: UploadFile = File(...), session: AsyncSession = Depends(get_session)):

    df = pd.read_excel(file.file)

    # iterate rows
    for _, row in df.iterrows():
        # insert expense
        payer = await session.execute(
            select(User).where(User.username == row["Payer"])
        )
        payer = payer.scalars().first()
        
        if not payer:
            raise HTTPException(status_code=400, detail=f"Payer {row['Payer']} not found")
        
        expense = Expense(
            group_id=group_id,
            payer_id=payer.id,   # ✅ use the id
            description=row["Name"],
            amount=row["Paid"],
            currency="MAD",
            created_at=datetime.now()
        )

        session.add(expense)
        await session.flush()  # get expense.id

        # insert splits for participants
        for participant in df.columns[3:]:  # participant columns
            if row[participant]:
                partis= await get_user_by_username(session, participant)
                user_id = partis.id
                share = expense.amount / row[3:].sum()
                session.add(Split(expense_id=expense.id, user_id=user_id, share_amount=share))
    
    await session.commit()
    return {"status": "success"}


@app.get("/groups/{group_id}/expenses/download")
async def download_expenses(
    group_id: int,
    session: AsyncSession = Depends(get_session),
    current = Depends(get_current_user)
):
    # 1) Query expenses with splits and split.user eagerly loaded
    stmt = (
        select(Expense)
        .where(Expense.group_id == group_id)
        .options(
            selectinload(Expense.splits).selectinload(Split.user)
        )
    )
    result = await session.execute(stmt)
    expenses = result.scalars().all()

    # 👉 get all participants of the group via Membership
    participants_res = await session.execute(
        select(User.username)
        .join(Membership, Membership.user_id == User.id)
        .where(Membership.group_id == group_id)
    )
    all_participants = [p for (p,) in participants_res.all()]

    # 2) Build rows
    rows = []
    for e in expenses:
        payer_username = None
        if e.payer_id:
            payer_res = await session.execute(select(User.username).where(User.id == e.payer_id))
            payer_username = payer_res.scalar_one_or_none() or f"User {e.payer_id}"

        expense_participants = {s.user.username for s in e.splits if s.user}
        distributions = [f"{float(s.share_amount):.2f} {e.currency}" for s in e.splits]

        category = getattr(e, "category", "") or ""
        settled = getattr(e, "settled", "") or ""

        base = {
            "ID": e.id,
            "Name": e.description,
            "Paid": f"{float(e.amount):.2f} {e.currency}",
            "Payer": payer_username or "",
            "Cost Distribution": " , ".join(distributions),
            "Category": category,
            "Settled": settled,
            "Created At": e.created_at.isoformat() if getattr(e, "created_at", None) else ""
        }

        # dynamic participant columns
        for p in all_participants:
            base[p] = "TRUE" if p in expense_participants else "FALSE"

        rows.append(base)

    # 3) DataFrame
    df = pd.DataFrame(
        rows,
        columns=[
            "ID","Name","Paid","Payer","Cost Distribution","Category","Settled","Created At", *all_participants
        ]
    )

    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    filename = f"group_{group_id}_expenses.xlsx"
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
