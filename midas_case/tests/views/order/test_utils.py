import time
from django.test import TransactionTestCase
from midas_case.api.order.utils import buy_process, sell_process
from midas_case.tests.helper import generator
from midas_case.models import AppleUser
from midas_case.constants import BUY_ORDER, SELL_ORDER
from midas_case.utils import get_remaining_apples


class UtilTests(TransactionTestCase):
    def setUp(self):
        username = 'test'
        password = 'PasSwOrD123*'

        self.user = AppleUser.objects.create_user(username=username, password=password)
        self.planned_number_of_apples = 2

    def test_buy_and_sell_process(self):
        from midas_case.api.order.utils import buy_process

        before_number_of_apples = get_remaining_apples()
        self.order = generator.create_order(user=self.user, type=BUY_ORDER,
                                            planned_number_of_apples=self.planned_number_of_apples)
        for i in range(self.planned_number_of_apples):
            buy_process({"id": str(self.order.id)})

        self.assertEqual(get_remaining_apples(), before_number_of_apples - self.planned_number_of_apples)

        self.order = generator.create_order(user=self.user, type=SELL_ORDER,
                                            planned_number_of_apples=self.planned_number_of_apples)
        for i in range(self.planned_number_of_apples):
            sell_process({"id": str(self.order.id)})

        self.assertEqual(get_remaining_apples(), before_number_of_apples)
