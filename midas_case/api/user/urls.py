from django.urls import path
from .views import Register, Login, Logout, RetrieveUser

urlpatterns = [
    path('users/register', Register.as_view(), name='register'),
    path('users/login', Login.as_view(), name='login'),
    path('users/logout', Logout.as_view(), name='logout'),
    path('user/', RetrieveUser.as_view(), name='retrieve_user'),
]