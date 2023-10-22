from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid


class CustomUser(AbstractUser):
    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4
    )

    date_joined = models.DateTimeField(default=timezone.now)