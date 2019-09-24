from rest_framework import viewsets
from core.models import *
from .serializer import *
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from binance.client import Client
from rest_framework import status
from django.shortcuts import get_object_or_404
import json
from binance.enums import *
from time import sleep
import sys
import math
import logging

PAGE_SIZE = 20
'''
    トークン取得処理
'''
class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        user = User.objects.get(id = token.user_id)
        return Response({'token': token.key, 'id': user.id, 'api_key': user.api_key, 'api_secret_key': user.api_secret_key, 'currency': user.currency })

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

class OrderSequenceViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = OrderSequence.objects.all()
    serializer_class = OrderSequenceSerializer

    def list(self, request):
        currency = request.user.currency
        qs = OrderSequence.objects.all()
        page_count = math.ceil(len(qs) / PAGE_SIZE)

        if currency != None and currency != '':
            qs = qs.filter(t1__from_currency = currency)   

        # pagination
        page = request.GET.get('page')
        if page:
            offset = (int(page) - 1) * PAGE_SIZE
            qs = qs[offset:offset + PAGE_SIZE] 
             
        data = OrderSequenceSerializer(qs, many=True).data
        # http response として返す
        return Response(status=200, data={ 'page_count': page_count, 'result': data })

    # 想定のシナリオを返す
    def retrieve(self, request, pk=None):
        obj = get_object_or_404(OrderSequence, id = pk)
        scenario = Scenario(obj, request.user)
        scenario.estimate()
        if not scenario.is_valid:
            return Response(status=200, data={'error': scenario.error_message})
        else:
            data = ScenarioSerializer(scenario, many= False).data
            return Response(status=200, data = data)
         
class OrderSequenceResultViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = OrderSequence.objects.all()
    serializer_class = OrderSequenceResultSerializer
   
    def list(self, request):
        qs = OrderSequenceResult.objects.filter(user = request.user).order_by('-t3_result__time')
        page_count = math.ceil(len(qs) / PAGE_SIZE)
        # pagination
        page = request.GET.get('page')
        if page:
            offset = (int(page) - 1) * PAGE_SIZE
            qs = qs[offset:offset + PAGE_SIZE] 
        
        data = OrderSequenceResultSerializer(qs, many=True).data
        return Response(status=200, data={ 'page_count': page_count, 'result': data })
    
    def create(self, request):
        logger = logging.getLogger('online')
        orderseq_id = request.data.get('orderseq_id')
        obj = get_object_or_404(OrderSequence, id = orderseq_id)
        
        scenario = Scenario(obj, request.user)
        scenario.estimate()
        if not scenario.is_valid:
            return Response(status=200, data={'error': scenario.error_message})
        scenario.execute()
        if not scenario.is_valid:
            return Response(status=200, data={ 'error': scenario.error_message })
        return Response(status=200, data={ 'success': True })


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = OrderSequence.objects.all()
    serializer_class = OrderSerializer
    
    def list(self, request):
        qs = Order.objects.filter(user = request.user).order_by('-time')
        page_count = math.ceil(len(qs) / PAGE_SIZE)
        # pagination
        page = request.GET.get('page')
        if page:
            offset = (int(page) - 1) * PAGE_SIZE
            qs = qs[offset:offset + PAGE_SIZE]
        print(len(qs))
        data = OrderSerializer(qs, many=True).data
        return Response(status=200, data={ 'page_count': page_count, 'result': data })
class BalanceView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request, format=None):
        client = Client(request.user.api_key, request.user.api_secret_key)
        balances = [asset for asset in client.get_account().get('balances') if float(asset.get("free")) > 0 or float(asset.get("locked")) > 0]
        data = BalanceSerializer(balances, many=True).data
        return Response(status=200, data=data)