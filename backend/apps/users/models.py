from django.conf import settings
from django_countries.fields import CountryField
from django.dispatch import receiver
from django_fsm.signals import post_transition
import re
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
# import secrets

# from apps.trafficsource.models import Campaign
CURRENCY_CHOICES = (
    ('USD', 'USD'),
    ('EUR', 'EUR')
)
TIMEZONE_CHOICES = (
    ('Asia/Jerusalem', '(UTC+02:00) Jerusalem'),
    ('Europe/Amsterdam', '(UTC+01:00) Amsterdam'),
)


class UserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        user = self.model(email=self.normalize_email(email),
                          is_active=True,
                          is_staff=is_staff,
                          is_superuser=is_superuser,
                          last_login=timezone.now(),
                          registered_at=timezone.now(),
                          **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        is_staff = extra_fields.pop('is_staff', False)
        is_superuser = extra_fields.pop('is_superuser', False)
        return self._create_user(email, password, is_staff, is_superuser, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, is_staff=True, is_superuser=True, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='Email',
                              unique=True, max_length=255)
    first_name = models.CharField(
        verbose_name='First name', max_length=30, default='first')
    last_name = models.CharField(
        verbose_name='Last name', max_length=30, default='last')

    is_admin = models.BooleanField(verbose_name='Admin', default=False)
    is_active = models.BooleanField(verbose_name='Active', default=True)
    is_staff = models.BooleanField(verbose_name='Staff', default=False)
    registered_at = models.DateTimeField(
        verbose_name='Registered at', auto_now_add=timezone.now)

    # Fields settings
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'

    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    @property
    def username(self):
        return self.email
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    @property
    def short_name(self):
        return self.first_name


class UserProfile(models.Model):
    # One-to-one relationship with the User model
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    first_name = models.CharField(
        verbose_name='First name', max_length=30, default='first')
    last_name = models.CharField(
        verbose_name='Last name', max_length=30, default='last')

    company_name = models.CharField(verbose_name='Company Name', max_length=30)
    country = CountryField(verbose_name='Country')
    telegram = models.CharField(
        verbose_name='Telegram Username', max_length=30, blank=True)
    skype = models.CharField(
        verbose_name='Skype Username', max_length=30, blank=True)
    status = models.BooleanField(verbose_name='Status', default=True)

    # Meta class
    class Meta:
        verbose_name = 'UserProfile'
        verbose_name_plural = 'UserProfiles'

    def __str__(self):
        return f"{self.user.email} - {self.company_name}"
