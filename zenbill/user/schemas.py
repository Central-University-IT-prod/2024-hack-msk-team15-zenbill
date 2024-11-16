from shelve import Shelf
from typing import Optional, List

from ninja import Schema


class UserUp(Schema):
    email: str
    name: str
    last_name: str
    password: str


class UserIn(Schema):
    email: str
    password: str


class UserOutSelf(Schema):
    email: str
    last_name: str
    name: str
    rating: float
    avatar_url: Optional[str]
    user_id: int

class UserOut(Schema):
    last_name: str
    name: str
    rating: float
    avatar_url: Optional[str]
    user_id: int

class ChangePassEmailStatus(Schema):
    status: str
    changed: bool


class ChangeEmail(Schema):
    password: str
    new_email: str

class ChangePassword(Schema):
    old_password: str
    new_password: str


class GroupCreation(Schema):
    name: str

class GroupCreationOut(Schema):
    group_id: int

class GroupAdd(Schema):
    group_id: int
    user_id: int

class GroupOut(Schema):
    group_id: int
    name: str
    members_id: Optional[List[int]] = []
    bills_ids: Optional[List[int]] = []

class GroupOutList(Schema):
    groups: List[GroupOut]


class OtherUserOut(Schema):
    last_name: str
    name: str
    rating: float

class OtherUserIn(Schema):
    user_id: int

class PayDebtIn(Schema):
    debt_id: int
    paid_price: int


class AddFriendIn(Schema):
    target_user: int

class FriendOut(Schema):
    last_name: str
    name: str
    rating: float
    user_id: int

class FriendOutList(Schema):
    friends: List[FriendOut]
