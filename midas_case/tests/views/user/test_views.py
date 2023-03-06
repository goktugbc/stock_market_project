import json

from django.test import TestCase
from django.http import HttpRequest
from django.urls.base import reverse
from midas_case.models import AppleUser, Order


class UserViewTests(TestCase):
    def setUp(self):
        self.username = 'test'
        self.password = 'PasSwOrD123*'

        self.login_username = 'login_user'
        self.login_password = 'PasSwOrD123*'

        self.login_user = AppleUser.objects.create_user(username=self.login_username, password=self.login_password)

    def test_register_view(self):
        request_body = {
            "username": self.username,
            "password": self.password,
            "password_conf": self.password
        }

        response = self.client.post(
            reverse('register'),
            json.dumps(request_body),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)

        json_string = response.content
        response_data = json.loads(json_string)

        self.assertEqual(response_data["username"], self.username)

    def test_missing_credentials_login_view(self):
        request_body = {
        }

        response = self.client.post(
            reverse('login'),
            json.dumps(request_body),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

        json_string = response.content
        response_data = json.loads(json_string)

        self.assertEqual(response_data["msg"], "Credentials missing")

    def test_successful_login_view(self):
        request_body = {
            "username": self.login_username,
            "password": self.login_password
        }

        response = self.client.post(
            reverse('login'),
            json.dumps(request_body),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        json_string = response.content
        response_data = json.loads(json_string)

        self.assertEqual(response_data["msg"], "Login Success")

    def test_unsuccessful_login_view(self):
        request_body = {
            "username": self.login_username,
            "password": self.login_password + "1"
        }

        response = self.client.post(
            reverse('login'),
            json.dumps(request_body),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 401)

        json_string = response.content
        response_data = json.loads(json_string)

        self.assertEqual(response_data["msg"], "Invalid Credentials")

    def test_retrieve_user_view(self):
        login = self.client.login(request=HttpRequest(),
                                  username=self.login_username,
                                  password=self.login_password)

        response = self.client.get(
            reverse('retrieve_user'),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        json_string = response.content
        response_data = json.loads(json_string)

        self.assertEqual(response_data["username"], self.login_username)
        self.assertEqual(response_data["number_of_apples"], self.login_user.get_number_of_apples())

    def test_unauthorized_retrieve_user_view(self):

        response = self.client.get(
            reverse('retrieve_user'),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 401)

        json_string = response.content
        response_data = json.loads(json_string)

        self.assertEqual(response_data["msg"], "Please login.")
