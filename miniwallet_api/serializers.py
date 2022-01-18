from dataclasses import field, fields
from rest_framework import serializers
from .models import User, Wallet, Transaction

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = '__all__'

class WalletSerializer(serializers.ModelSerializer):
  class Meta:
    model = Wallet
    fields = [
      'id',
      'owned_by',
      'status',
      'enable_at',
      'disable_at', 
      'balance'
    ]

class TransactionSerializer(serializers.ModelSerializer):
  class Meta:
    model = Transaction
    fields = [
        "id",
        "type",
        "withdrawn_by",
        "deposited_by",
        "status",
        "withdrawn_at",
        "deposited_at",
        "amount",
        "reference_id",
    ]