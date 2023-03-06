import os
import django
from celery import Celery
from django.utils import timezone
from datetime import timedelta
from midas_case import settings
from midas_case.event_streamer import EventStreamer
from midas_case.utils import get_remaining_apples
from midas_case.constants import APPLE_STOCK


app = Celery('midas_case')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'midas_case.settings')

django.setup()

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(queue="celery")
def buy():
    from midas_case.api.order.utils import buy_process
    event_streamer = EventStreamer("buy")
    event_streamer.create_consumer()
    message_count_to_process = APPLE_STOCK - get_remaining_apples()
    event_streamer.process_messages(buy_process, message_count_to_process)
    return True


@app.task(queue="celery")
def sell():
    from midas_case.api.order.utils import sell_process
    event_streamer = EventStreamer("sell")
    event_streamer.create_consumer()
    event_streamer.process_messages(sell_process)
    buy.apply_async(args=[], serializer="json", eta=timezone.now() + timedelta(seconds=10))
    return True


@app.task(queue="celery")
def cancel():
    from midas_case.api.order.utils import cancel_order
    event_streamer = EventStreamer("cancel")
    event_streamer.create_consumer()
    event_streamer.process_messages(cancel_order)
    return True
