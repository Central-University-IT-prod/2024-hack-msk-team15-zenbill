from typing import List
from datetime import datetime

from pydantic import BaseModel
from ninja import Schema


class SignInSchema(BaseModel):
    email: str
    password: str


class SignUpSchema(BaseModel):
    email: str
    password: str
    name: str
    last_name: str


class Debt(Schema):
    price: int
    paid: int


class DebtInList(Schema):
    price: int
    paided: int
    bill_name: str
    bill_expiration_date: str
    id: int
    bill_id: int
    name_second_user: str
    last_name_second_user: str


class DebtsList(Schema):
    debts: List[DebtInList]


class BillCreateSchema(BaseModel):
    name: str
    description: str
    group_id: int
    sum_debts: int
    expiration_date: datetime


class BillOut(BaseModel):
    id: int
    name: str
    description: str
    sum_debts: int
    expiration_date: str
    creation_date: str
    creator_id: int
    group_id: int
    debts: List[dict]

class BillListOut(BaseModel):
    bills: List[BillOut]

class DebtCreate(BaseModel):
    price: int
    user_to_id: int
    bill_id: int

class DebtOut(BaseModel):
    id: int
    price: int
    paided: int
    user_to_id: int
    user_from_id: int