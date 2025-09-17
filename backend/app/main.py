### `backend/app/main.py`
from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from .db import engine, Base, get_session
from .config import settings
from .schemas import UserCreate, UserOut, Token, GroupCreate, GroupOut, ExpenseCreate, ExpenseOut, BalanceItem
from .crud import create_user, get_user_by_email, create_group, add_expense, compute_group_balances, get_users,get_expenses,get_groups,get_user_by_username
from .auth import authenticate, create_access_token, get_current_user
from .debt import minimize_cash_flow

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

        

@app.get("/health")
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



@app.post("/auth/login", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    user = await authenticate(session, form.username, form.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(user.username)
    return Token(access_token=token)




@app.post("/groups", response_model=GroupOut)
async def create_group_ep(payload: GroupCreate, session: AsyncSession = Depends(get_session), current=Depends(get_current_user)):
    group = await create_group(session, name=payload.name, currency=payload.currency, owner_id=current.id, member_ids=payload.member_ids)
    return GroupOut.model_validate(group)

@app.post("/expenses", response_model=ExpenseOut)
async def create_expense_ep(payload: ExpenseCreate, session: AsyncSession = Depends(get_session), current=Depends(get_current_user)):
    # Optional: validate current user is in group
    splits = [(s.user_id, s.share_amount) for s in payload.splits]
    try:
        exp = await add_expense(session, group_id=payload.group_id, payer_id=payload.payer_id, description=payload.description, amount=payload.amount, currency=payload.currency, splits=splits)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ExpenseOut.model_validate(exp)

@app.get("/users", response_model=list[UserOut])
async def fetch_users(session: AsyncSession = Depends(get_session), current=Depends(get_current_user)):
    # current is the logged-in user; route is protected
    return await get_users(session)

 
@app.get("/groups", response_model=list[UserOut])
async def fetch_groups(session: AsyncSession = Depends(get_session), current=Depends(get_current_user)):
    # current is the logged-in user; route is protected
    return await get_groups(session)

@app.get("/expenses", response_model=list[UserOut])
async def fetch_expenses(session: AsyncSession = Depends(get_session), current=Depends(get_current_user)):
    # current is the logged-in user; route is protected
    return await get_expenses(session)



@app.get("/groups/{group_id}/balances", response_model=list[BalanceItem])
async def group_balances(group_id: int, session: AsyncSession = Depends(get_session), current=Depends(get_current_user)):
    bals = await compute_group_balances(session, group_id)
    return [BalanceItem(user_id=uid, net=net) for uid, net in sorted(bals.items())]

@app.get("/groups/{group_id}/settlements")
async def group_settlements(group_id: int, session: AsyncSession = Depends(get_session), current=Depends(get_current_user)):
    bals = await compute_group_balances(session, group_id)
    return [s.model_dump() for s in minimize_cash_flow(bals)]



'''
@app.get("/users", response_model=list[BalanceItem])
async def group_balances(user_id: int, session: AsyncSession = Depends(get_session), current=Depends(get_current_user)):
    bals = await compute_group_balances(session, user_id)
    return [BalanceItem(user_id=uid, net=net) for uid, net in sorted(bals.items())]

 @app.get("/users", response_model=list[UserOut])
async def get_users():
    return [UserOut.model_validate(u) for u in users]
'''