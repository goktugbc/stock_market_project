from django.urls import path
from .views import Register

urlpatterns = [
    path('users/register', Register.as_view(), name='register'),
    #path('users/register', RetrieveUser.as_view(), name='retrieve_user'),
]