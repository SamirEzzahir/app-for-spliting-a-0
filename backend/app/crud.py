### `backend/app/crud.py`
from fastapi import HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from .models import User, Group, Membership, Expense, Split
from .utils import hash_password
from .schemas import MembershipOut, UserOut,GroupOut,ExpenseOut,UserUpdate


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

async def get_user_by_id(session: AsyncSession, user_id: int) -> UserOut:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserOut.model_validate(user)


async def update_user(session: AsyncSession, user_id: int, data: UserUpdate) -> UserOut:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if data.username is not None:
        user.username = data.username
    if data.email is not None:
        user.email = data.email

    await session.commit()
    await session.refresh(user)
    return UserOut.model_validate(user)


async def delete_user(session: AsyncSession, user_id: int) -> None:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await session.delete(user)
    await session.commit()
    return None
   
   


# Create a group
async def create_group(session: AsyncSession, *, name: str, currency: str, owner_id: int, member_ids: list[int]) -> Group:
    group = Group(name=name, currency=currency,owner_id=owner_id)
    session.add(group)
    await session.flush()
    # Ensure owner is in the group
    members = set(member_ids) | {owner_id}
    for uid in members:
        session.add(Membership(user_id=uid, group_id=group.id, is_admin=(uid == owner_id)))
    await session.commit()
    await session.refresh(group)
    return group

# Get all groups
async def get_groups(session: AsyncSession) -> list[UserOut]:
    result = await session.execute(select(Group))  # SELECT * FROM users
    groups = result.scalars().all()               # Get list of User objects
    return [GroupOut.model_validate(u) for u in groups]

# Get group by ID
async def get_group(session: AsyncSession, group_id: int) -> Group:
    result = await session.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

# Update a group
async def update_group(session: AsyncSession, group_id: int, name: str | None, currency: str | None) -> Group:
    group = await get_group(session, group_id)
    if name:
        group.name = name
    if currency:
        group.currency = currency
    await session.commit()
    await session.refresh(group)
    return group

# Delete a group
async def delete_group(session: AsyncSession, group_id: int):
    group = await get_group(session, group_id)
    await session.delete(group)
    await session.commit()

    




async def add_member_to_group(session: AsyncSession, group_id: int, user_id: int, is_admin: bool = False):
    # First check if the membership already exists
    result = await session.execute(
        select(Membership).where(Membership.group_id == group_id, Membership.user_id == user_id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing  # Already a member

    membership = Membership(group_id=group_id, user_id=user_id, is_admin=is_admin)
    session.add(membership)
    await session.commit()
    await session.refresh(membership)
    return membership
 

 
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


async def get_expenses(session: AsyncSession, group_id: int) -> list[ExpenseOut]:
     # Load expenses + splits eagerly
    result = await session.execute(
        select(Expense)
        .where(Expense.group_id == group_id)
        .options(selectinload(Expense.splits))
    )
    expenses = result.scalars().all()
    # Collect all user IDs for mapping to usernames
    user_ids = {e.payer_id for e in expenses} | {s.user_id for e in expenses for s in e.splits}

    users_result = await session.execute(
        select(User.id, User.username).where(User.id.in_(user_ids))
    )
    users = dict(users_result.all())  # map id -> username

    # Build response
    return [
        ExpenseOut(
            id=e.id,
            group_id=e.group_id,
            description=e.description,
            amount=e.amount,
            category=e.category,
            payer_id=e.payer_id,
            payer_username=users.get(e.payer_id, "Unknown"),  # <-- include username
            splits=e.splits,
        )
        for e in expenses
    ]


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    return (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()

async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    return (await session.execute(select(User).where(User.username == username))).scalar_one_or_none()

'''
async def create_group(session: AsyncSession, *, name: str, currency: str, owner_id: int, member_ids: list[int]) -> Group:
    group = Group(name=name, currency=currency, owner_id=owner_id)
    session.add(group)
    await session.flush()
'''


async def get_groupMembers(session: AsyncSession, group_id: int)->list[MembershipOut]:
    
     # Load Memberships with related User
    result = await session.execute(select(Membership).options(selectinload(Membership.user))  # eager load User
        .where(Membership.group_id == group_id)
    )
    memberships = result.scalars().all()

    # Build response with username
    out = []
    for m in memberships:
        out.append(MembershipOut.model_validate({
            "id": m.id,
            "user_id": m.user_id,
            "group_id": m.group_id,
            "is_admin": m.is_admin,
            "username": m.user.username if m.user else None
        }))
    return out


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
