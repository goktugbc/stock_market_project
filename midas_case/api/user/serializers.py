from rest_framework import serializers
from midas_case.models import AppleUser


class RegistrationSerializer(serializers.ModelSerializer):
    password_conf = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = AppleUser
        fields = ['username', 'password', 'password_conf']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        user = AppleUser(username=self.validated_data['username'])
        password = self.validated_data['password']
        password_conf = self.validated_data['password_conf']
        if password != password_conf:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        user.set_password(password)
        user.save()
        return user

class AppleUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppleUser
        fields = ['username', 'number_of_apples']