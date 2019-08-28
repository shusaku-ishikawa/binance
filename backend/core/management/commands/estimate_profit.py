import logging
import os
from django.utils import timezone
from django.core.management.base import BaseCommand
from core.models import *
from binance.client import Client
from api.modules.helpers import _get_ticker, _get_2nd_entry, _get_order_amount

class Command(BaseCommand):
    help = '利益を計算する'

    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        api_key = '17ckzmZUmU7jglRfmESIgDtE7a5TrfEB4Wz64h5oZ9Mi4bG1mvoJC2dtPQYeZYMf'
        api_secret_key = 'k21zTLm0aBAMokpawmvWtMlEOE9B87o7o6GXfUFlbOfD3Dx48TBgq5xz4e1vBG6H'
        client = Client(api_key, api_secret_key)
        
        # 対象のSymbol
        t1_symbol = 'ETHBTC'
        t1_side = 'sell'
        t2_symbol = 'ADABTC'
        t2_side = 'buy'
        t3_symbol = 'ADAETH'
        t3_side = 'sell'
        
        t1 = Symbol.objects.get(symbol = t1_symbol, side = t1_side)
        t2 = Symbol.objects.get(symbol = t2_symbol, side = t2_side)
        t3 = Symbol.objects.get(symbol = t3_symbol, side = t3_side)
        
        orderseq = OrderSequence.objects.get(t1 = t1, t2 = t2, t3 = t3)

        t1_price = _get_2nd_entry(client, t1)[0]
        t2_price = _get_2nd_entry(client, t2)[0]
        t3_price = _get_2nd_entry(client, t3)[0]
        
        A_amount = _get_order_amount(client, orderseq)
        B_amount = (A_amount * t1_price) if t1.is_sell else (A_amount / t1_price)
        C_amount = (B_amount * t2_price) if t2.is_sell else (B_amount / t2_price)
        A_amount_ret = (C_amount * t3_price) if t3.is_sell else (C_amount / t3_price)
        
        t1_order_amount = A_amount if t1.is_sell else (A_amount / t1_price)    
        
        # target → B → C → target
        print('元手{currency} {amount}'.format(currency = t1.quote_asset, amount = A_amount))
        print('t1は{symbol} {side} で{currency}を{amount}取得'.format(symbol = t1.symbol, side = t1.side, currency = t1.base_asset, amount = B_amount))
        print('t2は{symbol} {side} で{currency}を{amount}取得'.format(symbol = t2.symbol, side = t2.side, currency = t2.base_asset, amount = C_amount))
        print('t3は{symbol} {side} で{currency}を{amount}取得'.format(symbol = t3.symbol, side = t3.side, currency = t3.base_asset, amount = A_amount_ret))
        
