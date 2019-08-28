from rest_framework import routers
from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('get-token/', CustomObtainAuthToken.as_view(), name = 'get-token'),
    path('balance/', BalanceView.as_view(), name = 'balance')
]

router = routers.SimpleRouter()
router.register('users', UserViewSet)
router.register('ordersequences', OrderSequenceViewSet)
router.register('orders', OrderViewSet)
router.register('ordersequenceresults', OrderSequenceResultViewSet)

urlpatterns += router.urls
