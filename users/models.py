from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import datetime
import uuid

now = timezone.now()
naive_datetime = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=now.hour, minute=now.minute, second=now.second)
aware_datetime = timezone.make_aware(naive_datetime, timezone=timezone.get_current_timezone())

class CustomUser(AbstractUser):
    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4
    )

    date_joined = models.DateTimeField(default=aware_datetime)