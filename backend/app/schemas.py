### `backend/app/schemas.py`

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional
from datetime import datetime




class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

 

class GroupCreate(BaseModel):
    name: str
    currency: str = "dhs"
    member_ids: List[int] = []

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    currency: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class GroupOut(BaseModel):
    id: int
    name: str
    currency: str
    owner_id: int  
    model_config = ConfigDict(from_attributes=True)





class ExpenseSplitIn(BaseModel):
    user_id: int
    share_amount: float

    class Config:
        from_attributes = True 

class ExpenseSplitOut(BaseModel):
    user_id: int
    share_amount: float
    username: str | None = None   # ✅ optional now
    model_config = ConfigDict(from_attributes=True)

class ExpenseCreate(BaseModel):
    group_id: int
    description: str
    currency: str
    amount: float = Field(gt=0)
    splits: List[ExpenseSplitIn]

class ExpenseUpdate(BaseModel):
    description: str | None = None
    amount: float | None = None
    category: str | None = None
    settled: bool | None = None

class ExpenseOut(BaseModel):
    id: int
    group_id: int
    payer_id: int | None
    payer_username: str | None   # <-- add this
    description: str
    amount: float
    currency: str
    created_at: datetime
    splits: List[ExpenseSplitOut]
    model_config = ConfigDict(from_attributes=True)



class BalanceItem(BaseModel):
    user_id: int
    username: str
    net: float  # positive means others owe this user, negative means this user owes

class SettlementOut(BaseModel):
    from_id: int
    from_username: str
    to_id: int
    to_username: str
    amount: float



class MembershipOut(BaseModel):
    id: int
    user_id: int
    group_id: int
    is_admin: bool
    username: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class MembershipUpdate(BaseModel):
    is_admin: bool

class AddMemberPayload(BaseModel):
    user_id: int
    is_admin: bool = False