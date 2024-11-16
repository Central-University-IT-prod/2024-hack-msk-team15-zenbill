from typing import Any

from django.core.exceptions import ValidationError
from django.http import Http404
from ninja import Router
from django.http.request import HttpRequest
from django.shortcuts import get_object_or_404
import jwt

from user.auth import AuthBearer
from user.models import User, Group
from conf.settings import SECRET_KEY
from .schemas import UserOut, ChangePassEmailStatus, ChangePassword, \
    GroupCreation, GroupCreationOut, GroupAdd, GroupOut, GroupOutList, OtherUserOut, ChangeEmail, \
    AddFriendIn, FriendOut, FriendOutList

router = Router()


def get_user(request) -> User:
    payload = jwt.decode(request.auth, SECRET_KEY, algorithms=['HS256'])
    user_id = payload['user_id']
    return get_object_or_404(User, id=user_id)


@router.get("/get_user", auth=AuthBearer(), response=UserOut)
def get_user_method(request: HttpRequest):
    user = get_user(request)

    avatar_url = user.avatar if user.avatar else None

    return UserOut(email=user.email,
                   last_name=user.last_name,
                   name=user.first_name,
                   rating=user.rating,
                   avatar_url=avatar_url,
                   user_id=user.id)


@router.get('/get_other_user{user_id}', auth=AuthBearer(), response=OtherUserOut)
def get_other_user(request, user_id: int):
    user = get_object_or_404(User, id=user_id)
    return OtherUserOut(last_name=user.last_name,
                        name=user.first_name,
                        rating=user.rating,
                        user_id=user.id)


@router.post('/change_pass', auth=AuthBearer(),
             response={200: ChangePassEmailStatus})
def change_pass(request, data: ChangePassword):
    user = get_user(request)
    if user.check_password(data.old_password):
        user.set_password(data.new_password)
        user.save()
        status = 'changed'
        changed = True
    else:
        status = 'password_not_correct'
        changed = False

    return ChangePassEmailStatus(status=status, changed=changed)


@router.post('/change_email', auth=AuthBearer(),
             response={200: ChangePassEmailStatus})
def change_login(request, data: ChangeEmail):
    user = get_user(request)
    if user.check_password(data.password):
        user.username = data.new_email
        user.email = data.new_email
        user.save()
        status = 'changed'
        changed = True
    else:
        status = 'password_not_correct'
        changed = False

    return ChangePassEmailStatus(status=status, changed=changed)


@router.post('/create_user_group', auth=AuthBearer(),
             response={200: GroupCreationOut})
def create_user_group(request, data: GroupCreation):
    user = get_user(request)
    group = Group(name=data.name, creator=user)
    group.save()

    try:
        group.full_clean()
    except ValidationError:
        return Http404

    user.friends_groups.add(group)
    user.save()

    return GroupCreationOut(group_id=group.id)


@router.get('/get_user_groups', auth=AuthBearer(), response=GroupOutList)
def get_user_groups(request):
    user = get_user(request)
    groups = user.friends_groups.all()

    formatted_groups = []
    for group in groups:
        members_id = list(group.members.values_list('id', flat=True))
        bills_id = list(group.bills.values_list('id', flat=True))

        formatted_groups.append(GroupOut(
            group_id=group.id, name=group.name,
            members_id=members_id,
            bills_id=bills_id))

    return GroupOutList(groups=formatted_groups)


@router.post('/group_user_add', auth=AuthBearer())
def add_user_in_group(request, data: GroupAdd) -> Any:
    group = get_object_or_404(Group, id=data.group_id)
    user = get_user(request)
    if user != group.creator:
        return {'detail': 'Пользователь не создатель группы'}
    target_user = get_object_or_404(User, id=data.user_id)

    group.members.add(target_user)
    group.save()
    return {'detail': 'Пользователь успешно добавлен в группу'}


@router.get('/get_group/{group_id}', response=GroupOut, auth=AuthBearer())
def get_group_with_bills(request, group_id: int):
    user = get_user(request)

    group = get_object_or_404(Group, id=group_id)

    if group not in user.friends_groups.all():
        raise Http404("Пользователь не состоит в этой группе")

    bills_ids = group.bills.values_list('id', flat=True)

    return GroupOut(
        group_id=group.id,
        name=group.name,
        creator_id=group.creator.id,
        members_id=list(group.members.values_list('id', flat=True)),
        bills_ids=list(bills_ids)
    )


@router.post('/add_friend', auth=AuthBearer())
def add_friend(request, data: AddFriendIn):
    user = get_user(request)
    user.friends.add(get_object_or_404(User, id=data.target_user))
    user.save()


@router.get('/get_friends', auth=AuthBearer(), response=FriendOutList)
def get_friends(request):
    user = get_user(request)
    friends = user.friends.all()

    formatted_friends = []
    for friend in friends:
        formatted_friends.append(FriendOut(
            last_name=friend.last_name,
            name=friend.first_name,
            rating=friend.rating,
            user_id=friend.id
        ))

    return FriendOutList(friends=formatted_friends)
