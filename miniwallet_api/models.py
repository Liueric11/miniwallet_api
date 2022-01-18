from cgitb import enable
from tkinter import CASCADE
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

# Create your models here.

class MyAccountManager(BaseUserManager):
  def create_user(self, id, password=None):

    user = self.model(id=id)
    user.save(using=self._db)
    return user
  
  def create_superuser(self, id, password=None):
    user = self.create_user(id=id, password=password)
    user.is_admin = True
    user.is_staff = True
    user.is_superuser = True
    user.save(using=self._db)
    return user


class User(AbstractBaseUser):
  customer_xid = models.CharField(max_length=200, unique=True, primary_key=True)
  password = models.CharField(max_length=200, null=True, blank=True, default="12345678")
  is_admin = models.BooleanField(default=False)
  is_staff = models.BooleanField(default=False)
  is_superuser = models.BooleanField(default=False)

  USERNAME_FIELD = 'customer_xid'

  objects = MyAccountManager()

  def __str__(self):
    return self.customer_xid
  
  def has_perm(self, obj=None):
    return self.is_admin
  
  def has_module_perms(self, app_label):
    return True

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
  if created:
    Token.objects.create(user=instance)

class Wallet(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4)
  owned_by = models.OneToOneField(User, on_delete=models.CASCADE)
  status = models.CharField(max_length=255, default="disable")
  enable_at = models.DateTimeField(null=True, blank=True)
  disable_at = models.DateTimeField(null=True, blank=True)
  balance = models.IntegerField(blank=True, default=0)

  def __str__(self):
    return str(self.id)

class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    type = models.CharField(max_length=255, null=True, blank=True)
    withdrawn_by = models.CharField(max_length=255, null=True, blank=True)
    deposited_by = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255)
    withdrawn_at = models.DateTimeField(null=True, blank=True)
    deposited_at = models.DateTimeField(null=True, blank=True)
    amount = models.IntegerField(default=0)
    reference_id = models.CharField(max_length=255, unique=True)

    def str(self):
        return self.reference_id