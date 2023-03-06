from rest_framework import serializers
from midas_case.models import AppleUser


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = AppleUser
        fields = ['username', 'password']


class RegistrationSerializer(serializers.ModelSerializer):
    password_conf = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = AppleUser
        fields = ['username', 'password', 'password_conf']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        password = self.validated_data['password']
        password_conf = self.validated_data['password_conf']
        if password != password_conf:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        user = AppleUser.objects.create_user(self.validated_data['username'], self.validated_data['password'])
        return user

class AppleUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppleUser
        fields = ['username', 'number_of_apples']