from django.utils import timezone

from ninja import Router
from django.http.request import HttpRequest
from django.http.response import JsonResponse, Http404
from django.shortcuts import get_object_or_404
import jwt
from django.forms.models import model_to_dict

from user.auth import AuthBearer
from user.models import User
from conf.settings import SECRET_KEY
from user.api import get_user
from bills.models import Bill, Debt, Group
from bills.schemas import DebtInList, DebtsList, BillCreateSchema, BillOut, \
    DebtOut, DebtCreate
from user.schemas import GroupOut, PayDebtIn

router = Router()


@router.get('/get_user_debts_from', auth=AuthBearer(), response=DebtsList)
def get_user_debts_from(request) -> DebtsList:
    user = get_user(request)

    debts = list(Debt.objects.filter(user_from=user.id).values(
        'price', 'paided', 'bill__name', 'bill__expiration_date', 'id',
        'bill__id', 'user_from__first_name', 'user_from__last_name'
    ))

    formatted_debts = []

    for debt in debts:
        formatted_debts.append(
            DebtInList(price=debt['price'], paided=debt['paided'],
                       bill_id=debt['bill__id'], id=debt['id'],
                       bill_name=debt['bill__name'],
                       bill_expiration_date=str(
                           debt['bill__expiration_date']),
                       name_second_user=debt[
                           'user_from__first_name'],
                       last_name_second_user=debt[
                           'user_from__last_name']))

    return DebtsList(debts=formatted_debts)


@router.get('/get_user_debts_to', auth=AuthBearer(), response=DebtsList)
def get_user_debts_to(request) -> DebtsList:
    user = get_user(request)

    debts = list(Debt.objects.filter(user_to=user.id).values(
        'price', 'paided', 'bill__name', 'bill__expiration_date', 'id',
        'bill__id', 'user_to__first_name', 'user_to__last_name'
    ))

    formatted_debts = []
    for debt in debts:
        formatted_debts.append(
            DebtInList(price=debt['price'], paided=debt['paided'],
                       bill_id=debt['bill__id'], id=debt['id'],
                       bill_name=debt['bill__name'],
                       bill_expiration_date=str(
                           debt['bill__expiration_date']),
                       name_second_user=debt[
                           'user_to__first_name'],
                       last_name_second_user=debt[
                           'user_to__last_name']))

    return DebtsList(debts=formatted_debts)


@router.post('/create_bill', auth=AuthBearer())
def create_bill(request, data: BillCreateSchema):
    user = get_user(request)

    group = get_object_or_404(Group, id=data.group_id)

    if not group.members.filter(id=user.id).exists():
        return JsonResponse({'detail': 'Пользователь не член группы'},
                            status=400)

    bill = Bill.objects.create(
        name=data.name,
        description=data.description,
        creator=user,
        group=group,
        sum_debts=data.sum_debts,
        expiration_date=data.expiration_date,
        creation_date=timezone.now()
    )

    return JsonResponse(
        {'bill_id': bill.id, 'message': 'Счет успешно создан'},
        status=201)


@router.get('/get_bill/{bill_id}', response=BillOut, auth=AuthBearer())
def get_bill(request, bill_id: int):
    user = get_user(request)

    bill = get_object_or_404(Bill, id=bill_id)

    if bill.group not in user.friends_groups.all():
        raise Http404('Пользователь не имеет доступа к счету')

    debts = list(bill.debts.all().values('id', 'price', 'paided', 'user_to_id',
                                         'user_from_id'))

    bill_data = BillOut(
        id=bill.id,
        name=bill.name,
        description=bill.description,
        sum_debts=bill.sum_debts,
        expiration_date=bill.expiration_date.isoformat(),
        creation_date=bill.creation_date.isoformat(),
        creator_id=bill.creator.id,
        group_id=bill.group.id,
        debts=debts
    )

    return bill_data


@router.post('/create_debt', response=DebtOut, auth=AuthBearer())
def create_debt(request, data: DebtCreate):
    user = get_user(request)

    bill = get_object_or_404(Bill, id=data.bill_id)
    if bill.group not in user.friends_groups.all():
        raise Http404('Пользователь не имеет доступа к группе')

    user_to = get_object_or_404(User, id=data.user_to_id)
    if bill.group not in user_to.friends_groups.all():
        raise Http404(
            'Должник не имеет доступа к группе')

    debt = Debt.objects.create(
        price=data.price,
        paided=0,
        bill=bill,
        user_to_id=data.user_to_id,
        user_from=user,
    )

    return DebtOut(
        id=debt.id,
        price=debt.price,
        paided=debt.paided,
        user_to_id=debt.user_to.id,
        user_from_id=debt.user_from.id,
    )

@router.post('/pay_debt', auth=AuthBearer())
def pay_debt(request, data: PayDebtIn):
    user = get_user(request)
    debt = get_object_or_404(Debt, id=data.debt_id)
    if debt.user_to != user:
        raise Http404('Пользователь не является плательщиком этого долга')

    debt.paided += data.paid_price
    debt.bill.sum_debts += data.paid_price
    debt.bill.save()

    if debt.paided > debt.price:
        debt.paided = debt.price

    debt.save()
