import logging
import os
from django.utils import timezone
from django.core.management.base import BaseCommand
from core.models import *
from binance.client import Client
from api.modules.helpers import _get_order_patterns, floating_decimals, round_by_step
from binance.enums import *

class Command(BaseCommand):
    help = 'アカウント情報を確認する'
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        api_key = '17ckzmZUmU7jglRfmESIgDtE7a5TrfEB4Wz64h5oZ9Mi4bG1mvoJC2dtPQYeZYMf'
        api_secret_key = 'k21zTLm0aBAMokpawmvWtMlEOE9B87o7o6GXfUFlbOfD3Dx48TBgq5xz4e1vBG6H'
        client = Client(api_key, api_secret_key)
        result = client.get_order_book(symbol = 'ETHBTC')
        bids = result.get('bids')
        asks = result.get('asks')
        bids = [bid[0] for bid in bids]
        asks = [ask[0] for ask in asks]
        print('bid: {} - {}'.format(bids[0], bids[len(bids) - 1]))
        print('ask: {} - {}'.format(asks[0], asks[len(asks) - 1]))
        