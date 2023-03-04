import uuid
import json

from django.utils import timezone
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UnicodeUsernameValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.utils import timezone
from midas_case.constants import ORDER_TYPES, BUY_ORDER, SELL_ORDER
from midas_case.event_streamer import EventStreamer


class AppleUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError('Users must have an username')

        user = self.model(
            username=self.username,
        )

        user.set_password(password)
        user.save()
        return user


class AppleUser(AbstractBaseUser):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        "username",
        max_length=150,
        unique=True,
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
        validators=[username_validator],
        error_messages={
            "unique": "A user with that username already exists.",
        },
    )
    number_of_apples = models.PositiveIntegerField(default=0)
    objects = AppleUserManager()

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username

    def get_number_of_apples(self):
        return self.number_of_apples

class Order(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(AppleUser, on_delete=models.CASCADE)
    type = models.CharField(choices=ORDER_TYPES, max_length=4)
    planned_number_of_apples = models.PositiveIntegerField(default=0)
    actual_number_of_apples = models.PositiveIntegerField(default=0)
    create_datetime = models.DateTimeField(default=timezone.now)
    closed_datetime = models.DateTimeField(default=None, blank=True, null=True)
    closed = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    result = models.TextField(default="", blank=True, null=True)

    def get_user(self):
        return self.user

    def get_cancelled(self):
        return self.cancelled

    def get_closed(self):
        return self.closed

    def get_actual_number_of_apples(self):
        return self.actual_number_of_apples

    def set_cancelled(self):
        self.cancelled = True
        self.closed = True
        self.closed_datetime = timezone.now()
        if self.actual_number_of_apples == 0:
            self.result = "Cancelled."
        elif self.actual_number_of_apples > 0:
            self.result = "Partially processed and cancelled."
        self.save()

    def set_closed(self, result=None):
        self.closed = True
        self.closed_datetime = timezone.now()
        self.result = result if result else "Completely processed and closed."
        self.save()

    def increment_actual_number_of_apples(self):
        self.actual_number_of_apples += 1
        self.save()
        if self.actual_number_of_apples == self.planned_number_of_apples:
            self.set_closed(True)

    def process_order(self):
        if self.type == BUY_ORDER:
            self.user.number_of_apples += 1
            self.user.save()
            self.increment_actual_number_of_apples()
        elif self.type == SELL_ORDER:
            self.user.number_of_apples -= 1
            self.user.save()
            self.increment_actual_number_of_apples()


# Signals
@receiver(post_save, sender=Order)
def produce_order_event(sender, instance, **kwargs):
    from midas_case.celery import buy, sell
    if kwargs['created']:
        event_streamer = EventStreamer(instance.type)
        event_streamer.create_producer()
        for i in range(instance.planned_number_of_apples):
            event_streamer.send_message({"id": str(instance.id)})
        buy.apply_async(args=[], serializer="json")
        sell.apply_async(args=[], serializer="json")
