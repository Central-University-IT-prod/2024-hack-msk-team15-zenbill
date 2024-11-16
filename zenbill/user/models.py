from django.contrib.auth.models import AbstractUser
from django.db import models


class Group(models.Model):
    name = models.CharField('имя', max_length=50)

    logo = models.ImageField('изображение', upload_to='images/groups_avatars', blank=True)
    creator = models.ForeignKey('User', on_delete=models.CASCADE)



class User(AbstractUser):
    rating = models.FloatField('рейтинг', default=0)
    friends = models.ManyToManyField(
        'self', verbose_name='друзья'
    )
    friends_groups = models.ManyToManyField(
        Group, verbose_name='группы', related_name='members'
    )

    avatar = models.ImageField('аватар', upload_to='images/users_avatars', blank=True)
