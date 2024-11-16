from django.db import models
from django.db.models import CharField

from django.apps import apps

from user.models import User, Group



class Bill(models.Model):
    name = models.CharField('имя', max_length=50)

    description = models.TextField('описание', max_length=150)

    creator = models.ForeignKey(
        User, verbose_name='создатель', on_delete=models.CASCADE
    )

    group = models.ForeignKey(Group, verbose_name='группа',
                              on_delete=models.CASCADE, related_name='bills')

    sum_debts = models.IntegerField('сумма долгов')
    expiration_date = models.DateTimeField('дата истечения')
    creation_date = models.DateTimeField('дата создания', auto_now_add=True)


class Debt(models.Model):
    price = models.IntegerField('долг')

    paided = models.IntegerField('заплачено')

    bill = models.ForeignKey('Bill', verbose_name='счет',
                             on_delete=models.CASCADE, related_name='debts')

    user_to = models.ForeignKey(
        User, verbose_name='долг кому', on_delete=models.CASCADE, related_name='debt_to', default=None
    )

    user_from = models.ForeignKey(
        User, verbose_name='долг от кого', on_delete=models.CASCADE, default=None
    )

