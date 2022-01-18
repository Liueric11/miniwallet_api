import datetime
from urllib import response
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import uuid
from .serializers import UserSerializer, WalletSerializer, TransactionSerializer
from rest_framework.authtoken.models import Token
from .models import Wallet

# Create your views here.
@api_view(['POST'])
def initialize(request):
  if request.method == 'POST':
    serializer = UserSerializer(data=request.data)
    data = {}
    if serializer.is_valid():
      user = serializer.save()
      token = Token.objects.get(user=user).key
      data['data'] = {"token": token}
      data['status'] = "success"
      Wallet.objects.create(owned_by = user)
    else:
      data = serializer.errors
    return Response(data)

@api_view(['PATCH', 'POST', 'GET'])
@permission_classes([IsAuthenticated])
def manage_wallet(request):
  token = Token.objects.get(key=request.META['HTTP_AUTHORIZATION'][6:])
  wallet = Wallet.objects.get(owned_by_id = token.user_id)
  if request.method == 'POST':
    if wallet.status == 'disable':
      args_update = {
        "id": wallet.id,
        "owned_by": wallet.owned_by,
        "status": "enable",
        "enable_at": datetime.datetime.now().astimezone().replace(microsecond=0).isoformat(),
        "disable_at": None,
        "balance": int(wallet.balance)
      }
      serializer = WalletSerializer(instance=wallet, data=args_update)
      if serializer.is_valid():
        serializer.save()
        response = {
          "status": "success",
          "data": {
              "wallet": {
                "id": serializer.data["id"],
                "owned_by": serializer.data["owned_by"],
                "status": serializer.data["status"],
                "enabled_at": serializer.data["enable_at"],
                "balance": serializer.data["balance"],
            }
          },
        }
      else:
        response = {"status": "fail", "data": {"error": "not valid"}}
    else:
      response = {"status": "fail", "data": {"error": "Already enabled"}}
    return Response(response)

  elif request.method == 'PATCH':

    if wallet.status == 'enable':
      args_update = {
        "id": wallet.id,
        "owned_by": wallet.owned_by,
        "status": "disable",
        "disable_at": datetime.datetime.now().astimezone().replace(microsecond=0).isoformat(),
        "enable_at": None,
        "balance": int(wallet.balance)
      }
      serializer = WalletSerializer(instance=wallet, data=args_update)
      if serializer.is_valid():
        serializer.save()
        response = {
          "status": "success",
          "data": {
              "wallet": {
                "id": serializer.data["id"],
                "owned_by": serializer.data["owned_by"],
                "status": serializer.data["status"],
                "disabled_at": serializer.data["disable_at"],
                "balance": serializer.data["balance"],
            }
          },
        }
      else:
        response = {"status": "fail", "data": {"error": "not valid"}}
    else:
      response = {"status": "fail", "data": {"error": "Already disabled"}}
    return Response(response)
  
  else:
    if wallet != None:
      if wallet.status == "enable":
        response = {
          "status": "success",
          "data": {
            "wallet": {
              "id": wallet.id,
              "owned_by": wallet.owned_by.customer_xid,
              "status": wallet.status,
              "enable_at": wallet.enable_at,
              "balance": wallet.balance
            }
          },
        }
      else:
        response = {
          "status": "fail",
          "data": {
            "error": "Disabled"
          }
        }
    else:
      response = {
        "status": "fail",
        "data": {
          "error": "Disabled"
        }
      }
    return Response(response)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deposits(request):
  token = Token.objects.get(key=request.META['HTTP_AUTHORIZATION'][6:])
  wallet = Wallet.objects.get(owned_by_id = token.user_id)
  body = request.data
  if len(body) != 0:
    insertArgs = {
      "id": str(uuid.uuid4()),
      "type": "deposit",
      "withdrawn_by": None,
      "withdrawn_at": None,
      "deposited_at": datetime.datetime.now().astimezone().replace(microsecond=0).isoformat(),
      "status": "success",
      "deposited_by": token.user_id,
      "amount": body["amount"],
      "reference_id": body["reference_id"],
    }
    balanceNow = int(wallet.balance)
    balanceDeposits = int(body["amount"])
    balanceUpdated = balanceDeposits + balanceNow
    updateArgs = {
      "id": wallet.id,
      "owned_by": wallet.owned_by,
      "status": wallet.status,
      "enable_at": wallet.enable_at,
      "disable_at": wallet.disable_at,
      "balance": balanceUpdated,
    }
    serializer_wallet = WalletSerializer(instance=wallet, data=updateArgs)
    serializer_transaction = TransactionSerializer(data=insertArgs)
    if serializer_transaction.is_valid():
      serializer_transaction.save()
      response = {
        "status": "success",
        "data": {
          "deposit": {
            "id": serializer_transaction.data["id"],
            "deposited_by": serializer_transaction.data["deposited_by"],
            "status": serializer_transaction.data["status"],
            "deposited_at": serializer_transaction.data["deposited_at"],
            "amount": serializer_transaction.data["amount"],
            "reference_id": serializer_transaction.data["reference_id"],
          }
        },
      }
      if serializer_wallet.is_valid():
        serializer_wallet.save()
        return Response(response)
      else:
        response = {
          "status": "fail",
          "data": {
            "error": "updated fail",
          },
        }
        return Response(response)
  else:
    response = {
      "status": "fail",
      "data": {
          "error": "server Error",
      },
    }
    return Response(response)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdrawals(request):
  token = Token.objects.get(key=request.META['HTTP_AUTHORIZATION'][6:])
  wallet = Wallet.objects.get(owned_by_id = token.user_id)
  body = request.data
  if len(body) != 0:
    insertArgs = {
      "id": str(uuid.uuid4()),
      "type": "withdrawn",
      "deposited_at": None,
      "deposited_by": None,
      "withdrawn_at": datetime.datetime.now().astimezone().replace(microsecond=0).isoformat(),
      "status": "success",
      "withdrawn_by": token.user_id,
      "amount": body["amount"],
      "reference_id": body["reference_id"],
    }
    balanceNow = int(wallet.balance)
    balanceWithdrawn = int(body["amount"])
    balanceUpdated = balanceNow - balanceWithdrawn
    updateArgs = {
      "id": wallet.id,
      "owned_by": wallet.owned_by,
      "status": wallet.status,
      "enable_at": wallet.enable_at,
      "disable_at": wallet.disable_at,
      "balance": balanceUpdated,
    }
    serializer_wallet = WalletSerializer(instance=wallet, data=updateArgs)
    serializer_transaction = TransactionSerializer(data=insertArgs)
    if serializer_transaction.is_valid():
      serializer_transaction.save()
      response = {
        "status": "success",
        "data": {
          "deposit": {
            "id": serializer_transaction.data["id"],
            "withdrawn_by": serializer_transaction.data["withdrawn_by"],
            "status": serializer_transaction.data["status"],
            "withdrawn_at": serializer_transaction.data["withdrawn_at"],
            "amount": serializer_transaction.data["amount"],
            "reference_id": serializer_transaction.data["reference_id"],
          }
        },
      }
      if serializer_wallet.is_valid():
        serializer_wallet.save()
        return Response(response)
      else:
        response = {
          "status": "fail",
          "data": {
            "error": "updated fail",
          },
        }
        return Response(response)
    else:
      response = {
          "status": "fail",
          "data": {
              "error": "server Error",
          },
      }
      return Response(response)
  else:
    response = {
      "status": "fail",
      "data": {
        "error": "invalid form request",
      },
  }
  return Response(response)