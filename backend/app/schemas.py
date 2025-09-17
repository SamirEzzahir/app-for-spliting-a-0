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

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

 

class GroupCreate(BaseModel):
    name: str
    currency: str = "dhs"
    member_ids: List[int] = []

class GroupOut(BaseModel):
    id: int
    name: str
    currency: str
    owner_id: int  
    model_config = ConfigDict(from_attributes=True)

class ExpenseSplitIn(BaseModel):
    user_id: int
    share_amount: float = Field(gt=0)

class ExpenseCreate(BaseModel):
    group_id: int
    payer_id: int
    description: str
    amount: float = Field(gt=0)
    currency: str
    splits: List[ExpenseSplitIn]

class ExpenseOut(BaseModel):
    id: int
    group_id: int
    payer_id: int
    description: str
    amount: float
    currency: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class BalanceItem(BaseModel):
    user_id: int
    net: float  # positive means others owe this user, negative means this user owes

class Settlement(BaseModel):
    from_user: int
    to_user: int
    amount: float
