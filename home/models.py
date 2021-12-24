from django.db import models
from uuid import uuid4


class ContactRequest(models.Model):
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    email = models.CharField(max_length=75)
    phone = models.CharField(max_length=25)
    details = models.TextField()
    date = models.DateField(auto_now=True)
    uuid = models.UUIDField(default=uuid4, unique=True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name
