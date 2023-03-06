import json
from django.test import TestCase
from django.http import HttpRequest
from django.urls.base import reverse
from midas_case.models import AppleUser, Order
from midas_case.constants import BUY_ORDER
from midas_case.tests.helper import generator


class OrderViewTests(TestCase):
    def setUp(self):
        username = 'test'
        password = 'PasSwOrD123*'

        self.user = AppleUser.objects.create_user(username=username, password=password)

        login = self.client.login(request=HttpRequest(),
                                  username=username,
                                  password=password)
        self.assertTrue(login)

        username = 'test_2'
        password = 'PasSwOrD123*'

        self.second_user = AppleUser.objects.create_user(username=username, password=password)
        self.planned_number_of_apples = 2

        self.forbidden_order = generator.create_order(user=self.second_user, type=BUY_ORDER,
                                            planned_number_of_apples=self.planned_number_of_apples)

    def test_buy_view(self):
        request_body = {
            "planned_number_of_apples": self.planned_number_of_apples,
        }

        response = self.client.post(
            reverse('buy'),
            json.dumps(request_body),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 202)

        json_string = response.content
        response_data = json.loads(json_string)

        self.assertEqual(response_data["planned_number_of_apples"], self.planned_number_of_apples)
        self.assertEqual(response_data["user"], self.user.pk)

    def test_sell_view(self):
        request_body = {
            "planned_number_of_apples": self.planned_number_of_apples,
        }

        response = self.client.post(
            reverse('sell'),
            json.dumps(request_body),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 202)

        json_string = response.content
        response_data = json.loads(json_string)

        self.assertEqual(response_data["planned_number_of_apples"], self.planned_number_of_apples)
        self.assertEqual(response_data["user"], self.user.pk)

    def test_cancel_view(self):
        request_body = {
            "planned_number_of_apples": self.planned_number_of_apples,
        }

        response = self.client.post(
            reverse('buy'),
            json.dumps(request_body),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 202)

        request_body = {
            "id": str(Order.objects.filter(user=self.user)[0].id),
        }

        response = self.client.delete(
            reverse('cancel'),
            json.dumps(request_body),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 202)

    def test_retrieve_order_view(self):
        request_body = {
            "planned_number_of_apples": self.planned_number_of_apples,
        }

        response = self.client.post(
            reverse('buy'),
            json.dumps(request_body),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 202)

        order = Order.objects.filter(user=self.user)[0]
        response = self.client.get(
            reverse('retrieve_order', kwargs={'order_id': str(order.id)}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        json_string = response.content
        response_data = json.loads(json_string)

    def test_retrieve_order_view(self):
        request_body = {
            "planned_number_of_apples": self.planned_number_of_apples,
        }

        response = self.client.post(
            reverse('buy'),
            json.dumps(request_body),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 202)

        order = Order.objects.filter(user=self.user)[0]
        response = self.client.get(
            reverse('retrieve_order', kwargs={'order_id': str(order.id)}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        json_string = response.content
        response_data = json.loads(json_string)

        self.assertEqual(response_data["id"], str(order.id))
        self.assertEqual(response_data["type"], str(order.type))
        self.assertEqual(response_data["planned_number_of_apples"], order.planned_number_of_apples)
        self.assertEqual(response_data["actual_number_of_apples"], order.actual_number_of_apples)
        self.assertEqual(response_data["create_datetime"],
                         str(order.create_datetime.isoformat().replace("+00:00", "Z")))
        self.assertEqual(response_data["closed_datetime"],
                         str(order.closed_datetime.isoformat().replace("+00:00", "Z")) if order.closed_datetime
                         else None)
        self.assertEqual(response_data["closed"], order.closed)
        self.assertEqual(response_data["cancelled"], order.cancelled)
        self.assertEqual(response_data["result"], str(order.result))

    def test_forbidden_retrieve_order_view(self):
        request_body = {
            "planned_number_of_apples": self.planned_number_of_apples,
        }

        response = self.client.post(
            reverse('buy'),
            json.dumps(request_body),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 202)

        response = self.client.get(
            reverse('retrieve_order', kwargs={'order_id': str(self.forbidden_order.id)}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 403)

        json_string = response.content
        response_data = json.loads(json_string)

        self.assertEqual(response_data["msg"], "Wrong user.")

    def test_retrieve_orders_view(self):
        request_body = {
            "planned_number_of_apples": self.planned_number_of_apples,
        }

        response = self.client.post(
            reverse('buy'),
            json.dumps(request_body),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 202)

        response = self.client.get(
            reverse('retrieve_orders'),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

        json_string = response.content
        response_data = json.loads(json_string)

        self.assertEqual(len(response_data), Order.objects.filter(user=self.user).count())
