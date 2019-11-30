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
from django.db.models import Q

PAGE_SIZE = 20
'''
    トークン取得処理
'''
class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        user = User.objects.get(id = token.user_id)
        return Response({'token': token.key, 'id': user.id, 'api_key': user.api_key, 'api_secret_key': user.api_secret_key })

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
        base_currencies = ['BTC', 'ETH', 'USDT', 'BNB']
        qs = OrderSequence.objects.filter(t1__from_currency__in = base_currencies)
        if not request.user.do_btc:
            qs = qs.filter(~Q(t1__from_currency = 'BTC'))
        if not request.user.do_eth:
            qs = qs.filter(~Q(t1__from_currency = 'ETH'))
        if not request.user.do_usd:
            qs = qs.filter(~Q(t1__from_currency = 'USDT'))
        if not request.user.do_bnb:
            qs = qs.filter(~Q(t1__from_currency = 'BNB'))
           
        page_count = math.ceil(len(qs) / PAGE_SIZE)

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
        qs = OrderSequenceResult.objects.filter(user = request.user).order_by('-id')
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
        print('estimated:{} result:{}'.format(scenario.profit, scenario.result.profit))
        if not scenario.is_valid:
            return Response(status=200, data={ 'error': scenario.error_message })
        return Response(status=200, data={ 'success': True, 'profit': scenario.profit })


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
        data = BalanceSerializer(request.user.balances, many=True).data
        return Response(status=200, data=data)