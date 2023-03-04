import os
from celery import Celery
from midas_case import settings
from midas_case.event_streamer import EventStreamer


app = Celery('midas_case')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'midas_case.settings')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(queue="celery")
def buy():
    from midas_case.api.order.utils import buy_process
    event_streamer = EventStreamer("buy")
    event_streamer.create_consumer()
    event_streamer.process_messages(buy_process)


@app.task(queue="celery")
def sell():
    from midas_case.api.order.utils import sell_process
    event_streamer = EventStreamer("sell")
    event_streamer.create_consumer()
    event_streamer.process_messages(sell_process)


@app.task(queue="celery")
def cancel():
    from midas_case.api.order.utils import cancel_order
    event_streamer = EventStreamer("cancel")
    event_streamer.create_consumer()
    event_streamer.process_messages(cancel_order)
