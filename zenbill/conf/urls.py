from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from user.auth import router as auth_router
from user.api import router as user_router
from bills.api import router as bills_router

api = NinjaAPI()
api.add_router('/auth/', auth_router)
api.add_router('', user_router)
api.add_router('', bills_router)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls)
]
