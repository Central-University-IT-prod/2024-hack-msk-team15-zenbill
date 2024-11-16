from django.contrib.auth import get_user_model, authenticate
from ninja import Router
from ninja.security import django_auth
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from pydantic import BaseModel
from typing import Any, Dict

User = get_user_model()
router = Router()


# Схемы для регистрации и авторизации
class RegisterSchema(BaseModel):
    username: str
    password: str
    email: str


class AuthSchema(BaseModel):
    username: str
    password: str


class TokenResponseSchema(BaseModel):
    access: str
    refresh: str


@router.post("/register", response={201: Dict[str, Any], 400: Dict[str, str]})
def register(request, data: RegisterSchema):
    if User.objects.filter(username=data.username).exists():
        return 400, {"detail": "Пользователь с таким именем уже существует."}

    user = User.objects.create(
        username=data.username,
        password=make_password(data.password),
        email=data.email
    )
    return 201, {"detail": "Пользователь успешно зарегистрирован."}


@router.post("/token",
             response={200: TokenResponseSchema, 401: Dict[str, str]})
def login(request, data: AuthSchema):
    user = authenticate(username=data.username, password=data.password)
    if user:
        refresh = RefreshToken.for_user(user)
        return 200, {
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }
    else:
        return 401, {"detail": "Неправильные учетные данные"}