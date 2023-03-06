from django.test import TestCase
from midas_case.tests.helper import generator
from midas_case.models import AppleUser, Order
from midas_case.constants import BUY_ORDER, SELL_ORDER


class UserTests(TestCase):
    def test_create_user(self):
        username = 'test'
        password = 'PasSwOrD123*'

        user = AppleUser.objects.create_user(username=username, password=password)

        self.assertEqual(AppleUser.objects.count(), 1)
        self.assertTrue(isinstance(user, AppleUser))
        self.assertEqual(user.username, username)
        self.assertTrue(user.check_password(password))

    def test_create_user_with_none_username(self):
        username = None
        password = 'PasSwOrD123*'
        with self.assertRaises(ValueError) as raised:
            AppleUser.objects.create_user(username=username, password=password)
            self.assertEqual(ValueError, type(raised.exception))


class OrderTests(TestCase):
    def setUp(self):
        username = 'test'
        password = 'PasSwOrD123*'

        self.user = AppleUser.objects.create_user(username=username, password=password)

        self.order_type = BUY_ORDER
        self.planned_number_of_apples = 3

        self.order = generator.create_order(user=self.user, type=self.order_type,
                                            planned_number_of_apples=self.planned_number_of_apples)

    def test_create_order(self):
        self.assertEqual(Order.objects.count(), 1)
        self.assertTrue(isinstance(self.order, Order))
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.type, self.order_type)
        self.assertEqual(self.order.planned_number_of_apples, self.planned_number_of_apples)

    def test_order_get_user(self):
        self.assertEqual(self.order.get_user(), self.user)

    def test_order_get_cancelled(self):
        self.assertEqual(self.order.get_cancelled(), self.order.cancelled)

    def test_order_get_closed(self):
        self.assertEqual(self.order.get_closed(), self.order.closed)

    def test_order_get_actual_number_of_apples(self):
        self.assertEqual(self.order.get_actual_number_of_apples(), self.order.actual_number_of_apples)

    def test_order_set_cancelled_wo_partial_completion(self):
        self.order = generator.create_order(user=self.user, type=self.order_type,
                                            planned_number_of_apples=self.planned_number_of_apples)
        self.order.set_cancelled()

        self.assertTrue(self.order.get_cancelled())
        self.assertTrue(self.order.get_closed())
        self.assertNotEqual(self.order.closed_datetime, None)
        self.assertEqual(self.order.result, "Cancelled.")

    def test_order_set_cancelled_with_partial_completion(self):
        self.order = generator.create_order(user=self.user, type=self.order_type,
                                            planned_number_of_apples=self.planned_number_of_apples)
        self.order.increment_actual_number_of_apples()
        self.order.set_cancelled()

        self.assertTrue(self.order.get_cancelled())
        self.assertTrue(self.order.get_closed())
        self.assertNotEqual(self.order.closed_datetime, None)
        self.assertEqual(self.order.result, "Partially processed and cancelled.")

    def test_order_set_closed_wo_result(self):
        self.order = generator.create_order(user=self.user, type=self.order_type,
                                            planned_number_of_apples=self.planned_number_of_apples)
        self.order.set_closed()

        self.assertTrue(self.order.get_closed())
        self.assertNotEqual(self.order.closed_datetime, None)
        self.assertEqual(self.order.result, "Completely processed and closed.")

    def test_order_set_closed_with_result(self):
        test_result = "Test result"
        self.order = generator.create_order(user=self.user, type=self.order_type,
                                            planned_number_of_apples=self.planned_number_of_apples)
        self.order.set_closed(test_result)

        self.assertTrue(self.order.get_closed())
        self.assertNotEqual(self.order.closed_datetime, None)
        self.assertEqual(self.order.result, test_result)

    def test_order_set_result(self):
        test_result = "Test result"
        self.order = generator.create_order(user=self.user, type=self.order_type,
                                            planned_number_of_apples=self.planned_number_of_apples)
        self.order.set_result(test_result)

        self.assertEqual(self.order.result, test_result)

    def test_order_increment_actual_number_of_apples_and_closed(self):
        planned_number_of_apples = 1
        self.order = generator.create_order(user=self.user, type=self.order_type,
                                            planned_number_of_apples=planned_number_of_apples)
        self.order.increment_actual_number_of_apples()

        self.assertEqual(self.order.get_actual_number_of_apples(), planned_number_of_apples)
        self.assertTrue(self.order.get_closed())
        self.assertEqual(self.order.result, "Completely processed and closed.")

    def test_order_increment_actual_number_of_apples_and_not_closed(self):
        planned_number_of_apples = 2
        self.order = generator.create_order(user=self.user, type=self.order_type,
                                            planned_number_of_apples=planned_number_of_apples)
        self.order.increment_actual_number_of_apples()

        self.assertEqual(self.order.get_actual_number_of_apples(), 1)
        self.assertFalse(self.order.get_closed())
        self.assertEqual(self.order.result, "Partially processed.")

    def test_order_process_buy_and_sell_order(self):
        self.order = generator.create_order(user=self.user, type=BUY_ORDER,
                                            planned_number_of_apples=self.planned_number_of_apples)
        self.order.process_order()

        self.assertEqual(self.order.get_user().get_number_of_apples(), 1)

        self.order = generator.create_order(user=self.user, type=SELL_ORDER,
                                            planned_number_of_apples=self.planned_number_of_apples)
        self.order.process_order()

        self.assertEqual(self.order.get_user().get_number_of_apples(), 0)
