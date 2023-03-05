def calculate_remaining_apples():
    from django.db.models import Sum
    from midas_case.models import AppleUser
    from midas_case.constants import APPLE_STOCK

    remaining_apples = APPLE_STOCK - AppleUser.objects.aggregate(Sum('number_of_apples'))["number_of_apples__sum"]

    return remaining_apples


def set_remaining_apples(remaining_apples):
    import redis
    from midas_case.settings import CACHE_CONFIG

    redis_client = redis.StrictRedis(**CACHE_CONFIG)
    redis_client.set("remaining_apples", remaining_apples)

    return remaining_apples


def get_remaining_apples():
    import redis
    from midas_case.settings import CACHE_CONFIG

    redis_client = redis.StrictRedis(**CACHE_CONFIG)
    cache = redis_client.get("remaining_apples")
    if cache is not None:
        return int(cache)

    return int(set_remaining_apples(calculate_remaining_apples()))
