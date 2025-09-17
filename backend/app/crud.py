### `backend/app/crud.py`
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from .models import User, Group, Membership, Expense, Split
from .utils import hash_password
from .schemas import UserOut,GroupOut,ExpenseOut


async def create_user(session: AsyncSession, *, email: str, username: str, password: str) -> User:
    user = User(email=email, username=username, password_hash=hash_password(password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def get_users(session: AsyncSession) -> list[UserOut]:
    result = await session.execute(select(User))  # SELECT * FROM users
    users = result.scalars().all()               # Get list of User objects
    return [UserOut.model_validate(u) for u in users]

async def get_groups(session: AsyncSession) -> list[UserOut]:
    result = await session.execute(select(Group))  # SELECT * FROM users
    groups = result.scalars().all()               # Get list of User objects
    return [GroupOut.model_validate(u) for u in groups]


async def get_expenses(session: AsyncSession) -> list[UserOut]:
    result = await session.execute(select(Group))  # SELECT * FROM users
    expense = result.scalars().all()               # Get list of User objects
    return [ExpenseOut.model_validate(u) for u in expense]


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    return (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()

async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    return (await session.execute(select(User).where(User.username == username))).scalar_one_or_none()


async def create_group(session: AsyncSession, *, name: str, currency: str, owner_id: int, member_ids: list[int]) -> Group:
    group = Group(name=name, currency=currency)
    session.add(group)
    await session.flush()
    # Ensure owner is in the group
    members = set(member_ids) | {owner_id}
    for uid in members:
        session.add(Membership(user_id=uid, group_id=group.id, is_admin=(uid == owner_id)))
    await session.commit()
    await session.refresh(group)
    return group

async def add_expense(session: AsyncSession, *, group_id: int, payer_id: int, description: str, amount: float, currency: str, splits: list[tuple[int, float]]) -> Expense:
    exp = Expense(group_id=group_id, payer_id=payer_id, description=description, amount=amount, currency=currency)
    session.add(exp)
    await session.flush()
    total = 0.0
    for uid, share in splits:
        total += float(share)
        session.add(Split(expense_id=exp.id, user_id=uid, share_amount=share))
    if round(total, 2) != round(float(amount), 2):
        raise ValueError("Sum of splits must equal amount")
    await session.commit()
    await session.refresh(exp)
    return exp

 

async def group_member_ids(session: AsyncSession, group_id: int) -> list[int]:
    rows = await session.execute(select(Membership.user_id).where(Membership.group_id == group_id))
    return [r[0] for r in rows.all()]

async def compute_group_balances(session: AsyncSession, group_id: int) -> dict[int, float]:
    """Return net balance per user (positive = others owe them)."""
    # credits (payer paid for group): sum expenses by payer
    payer_rows = await session.execute(select(Expense.payer_id, func.sum(Expense.amount)).where(Expense.group_id == group_id).group_by(Expense.payer_id))
    credits: dict[int, float] = {uid: float(total or 0) for uid, total in payer_rows.all()}

    # debits (what each user owes by splits)
    split_rows = await session.execute(select(Split.user_id, func.sum(Split.share_amount)).join(Expense, Expense.id == Split.expense_id).where(Expense.group_id == group_id).group_by(Split.user_id))
    debits: dict[int, float] = {uid: float(total or 0) for uid, total in split_rows.all()}

    users = set(await group_member_ids(session, group_id)) | set(credits) | set(debits)
    balances = {uid: round(credits.get(uid, 0.0) - debits.get(uid, 0.0), 2) for uid in users}
    return balances
