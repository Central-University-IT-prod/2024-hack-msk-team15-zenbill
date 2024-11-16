from user.models import User
from django.test import TestCase
from http import HTTPStatus
from django.urls import reverse
import json
from django.contrib.auth import get_user_model
from bills.models import Debt, Bill
from ninja.testing import TestClient

from user.auth import router as auth_router
from user.schemas import UserUp


class UserSignUpApiTests(TestCase):
    def setUp(self):
        super().setUp()
        self.user_up = UserUp(
            email="duplicate@example.com",
            name="John",
            last_name="Doe",
            password="ValidPassword123",
        )

    def test_signup_users(self):
        client = TestClient(auth_router)
        data = self.user_up.dict()
        res = client.post("/signup", json.dumps(data), content_type="application/json")

        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.assertEqual(len(res.data), 1)


class UserSignInApiTests(TestCase):
    def setUp(self):
        # Создаем пользователя для теста
        self.user_data = {
            "email": "testuser@example.com",
            "password": "ValidPassword123",
            "name": "John",
            "last_name": "Doe"
        }
        # Регистрация пользователя
        self.user = User.objects.create_user(
            username=self.user_data["email"],
            email=self.user_data["email"],
            password=self.user_data["password"],
            first_name=self.user_data["name"],
            last_name=self.user_data["last_name"]
        )

        # URL для тестирования
        self.signin_url = '/api/auth/signin'  # Убедитесь, что используете правильный URL

    def test_signin_success(self):
        # Данные для входа
        signin_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }

        # Отправляем POST-запрос для входа
        response = self.client.post(
            self.signin_url,
            data=json.dumps(signin_data),  # Отправляем как JSON
            content_type='application/json'
        )

        # Проверяем, что ответ успешный и содержит токен
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("token", response_data)  # Проверяем, что в ответе есть токен

    def test_signin_invalid_credentials(self):
        # Данные для входа с неверным паролем
        signin_data = {
            "email": self.user_data["email"],
            "password": "WrongPassword123"
        }

        # Отправляем POST-запрос для входа
        response = self.client.post(
            self.signin_url,
            data=json.dumps(signin_data),  # Отправляем как JSON
            content_type='application/json'
        )

        # Проверяем, что ошибка 404, так как пользователь не найден или пароль неверный
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Not Found")

    def test_signin_user_not_found(self):
        # Данные для входа с несуществующим пользователем
        signin_data = {
            "email": "nonexistentuser@example.com",
            "password": "SomePassword123"
        }

        # Отправляем POST-запрос для входа
        response = self.client.post(
            self.signin_url,
            data=json.dumps(signin_data),  # Отправляем как JSON
            content_type='application/json'
        )

        # Проверяем, что ошибка 404, так как пользователь не найден
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Not Found")
