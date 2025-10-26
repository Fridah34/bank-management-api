# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CUSTOMER = "customer"
    ROLE_ADMIN = "admin"
    ROLE_CHOICES = (
        (ROLE_CUSTOMER, "Customer"),
        (ROLE_ADMIN, "Admin"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)

    def is_customer(self):
        return self.role == self.ROLE_CUSTOMER

    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    def __str__(self):
        return f"{self.username} ({self.role})"
