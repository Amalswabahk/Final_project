from django.db import models
from django.contrib.auth.models import User

from django.contrib.auth.models import AbstractUser
from django.db import models

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class User(AbstractUser):
    is_patient = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    # Fix reverse accessor clashes
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="custom_user_groups",
        related_query_name="custom_user"
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="custom_user_permissions",
        related_query_name="custom_user"
    )

    class Meta:
        db_table = 'custom_user'
        swappable = 'AUTH_USER_MODEL'

class Facility(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


from django.db import models
from django.utils.text import slugify


from django.db import models
from django.utils.text import slugify

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True,
                            help_text="Font Awesome icon class (e.g., 'fa-heart')")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Resource(models.Model):
    RESOURCE_TYPES = [
        ('ROOM', 'Room'),
        ('EQUIP', 'Equipment'),
        ('VEHICLE', 'Vehicle'),
        ('OTHER', 'Other'),
    ]

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='resources')
    name = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPES)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.get_resource_type_display()})"


from django.db import models

# Create your models here.
