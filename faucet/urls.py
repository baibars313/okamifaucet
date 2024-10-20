from django.urls import path
from .views import homepage, submit_faucet

urlpatterns = [
    path('', homepage, name='homepage'),
    path('submit/', submit_faucet, name='submit_faucet'),
]
