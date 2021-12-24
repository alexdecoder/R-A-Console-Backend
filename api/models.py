from django.db import models
from uuid import uuid4
from django.contrib.auth.models import User


class Job(models.Model):
    job_title = models.CharField(max_length=20)
    job_notes = models.TextField(blank=True)
    job_cost = models.DecimalField(decimal_places=2, max_digits=7)
    job_date = models.DateField(auto_created=True)
    job_paid = models.BooleanField(default=False)
    job_uuid = models.UUIDField(default=uuid4, unique=True, editable=False)
    job_category = models.IntegerField(default=-1)

    def __str__(self):
        try:
            customer = Customer.objects.get(jobs__id=self.id)
            return self.job_title + ' | ' + customer.first_name + ' ' + customer.last_name
        except Customer.DoesNotExist:
            return self.job_title


class Customer(models.Model):
    first_name = models.CharField(max_length=10)
    last_name = models.CharField(max_length=10)
    email = models.EmailField()
    number = models.CharField(max_length=14)
    uuid = models.UUIDField(default=uuid4, unique=True, editable=False)
    jobs = models.ManyToManyField(blank=True, to=Job)
    address = models.CharField(max_length=50)

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_id = models.UUIDField(default=uuid4, unique=True)
    date_time = models.DateTimeField(auto_now=True)
    is_valid = models.BooleanField(default=True)
    fcm_token = models.TextField()

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name + ' | ' + str(self.session_id)
