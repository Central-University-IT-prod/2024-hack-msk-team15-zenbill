import jwt
from django.contrib import auth
from django.http import Http404
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.security import HttpBearer
from http import HTTPStatus
from .models import User
from .schemas import UserUp, UserIn
from conf.settings import SECRET_KEY

router = Router()


class InvalidToken(Exception):
    pass


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            get_object_or_404(User, id=user_id)
        except jwt.ExpiredSignatureError:
            raise InvalidToken
        except jwt.InvalidTokenError:
            raise InvalidToken
        return token


@router.post('/signup')
def signup(request, user: UserUp):
    account = User.objects.create_user(username=user.email,
                                       email=user.email,
                                       password=user.password,
                                       first_name=user.name,
                                       last_name=user.last_name)
    account.save()

    encoded_jwt = jwt.encode({"user_id": account.id}, SECRET_KEY, algorithm="HS256")
    return 200, {"token": encoded_jwt}



@router.post('/signin')
def signin(request, user: UserIn):
    account = auth.authenticate(username=user.email, password=user.password)
    if account is not None:
        encoded_jwt = jwt.encode({"user_id": account.id}, SECRET_KEY, algorithm="HS256")
        return 200, {"token": encoded_jwt}
    else:
        raise Http404