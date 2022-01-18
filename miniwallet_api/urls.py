from django.urls import path
from . import views

urlpatterns = [
  path('v1/init', views.initialize, name="initialize"),
  path('v1/wallet', views.manage_wallet, name="manage_wallet"),
  path('v1/wallet/deposits', views.deposits, name="deposits"),
  path('v1/wallet/withdrawals', views.withdrawals, name="withdrawals"),
]