from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from midas_case.rest_framework_settings import CsrfExemptSessionAuthentication
from .serializers import LoginSerializer, RegistrationSerializer, AppleUserSerializer


class Register(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Login(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        if 'username' not in request.data or 'password' not in request.data:
            return Response({'msg': 'Credentials missing'}, status=status.HTTP_400_BAD_REQUEST)
        username = request.data['username']
        password = request.data['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({'msg': 'Login Success'}, status=status.HTTP_200_OK)
        return Response({'msg': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class Logout(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def get(self, request):
        logout(request)
        return Response({'msg': 'Successfully Logged out'}, status=status.HTTP_200_OK)


class RetrieveUser(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def get(self, request):
        if isinstance(request.user, AnonymousUser):
            return Response({'msg': 'Please login.'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            serializer = AppleUserSerializer(request.user)
            return Response(serializer.data)
