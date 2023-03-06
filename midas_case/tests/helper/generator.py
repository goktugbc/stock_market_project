from midas_case.models import AppleUser, Order


def create_order(user, type, planned_number_of_apples):
    return Order.objects.create(user=user, type=type, planned_number_of_apples=planned_number_of_apples)