from django.db import transaction, IntegrityError
from midas_case.models import Order
from midas_case.utils import get_remaining_apples


def buy_process(order_message):
    order = Order.objects.get(id=order_message["id"])
    if get_remaining_apples() > 0:
        try:
            with transaction.atomic():
                order.process_order()
        except IntegrityError:
            return False
    else:
        return False
    get_remaining_apples()
    return True


def sell_process(order_message):
    order = Order.objects.get(id=order_message["id"])
    if order.get_user().get_number_of_apples() > 0:
        try:
            with transaction.atomic():
                order.process_order()
        except IntegrityError:
            return False
    else:
        order.set_closed("No apple to sell.")
        return True
    get_remaining_apples()
    return True


def cancel_order(order_message):
    order = Order.objects.get(id=order_message["id"])

    if not order.get_closed():
        try:
            with transaction.atomic():
                order.set_cancelled()
        except IntegrityError:
            return False
    else:
        return True

    return True
