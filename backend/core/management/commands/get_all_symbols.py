import logging
import os
from django.utils import timezone
from django.core.management.base import BaseCommand
from core.models import *
from binance.client import Client
from api.modules.helpers import _get_order_patterns
from binance.enums import *

class Command(BaseCommand):
    help = '全てのシンボルを取得します'

    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        # symbol全て削除
        logger = logging.getLogger('batch')
        logger.info('START')
        Symbol.objects.all().delete()
        user = User.objects.all()[0]
        client = user.get_binance_client()
        if not client():
            logger.error('APIキーが登録されていません')
            return
        info = client.get_exchange_info()
        symbols = info.get('symbols')
        for symbol in symbols:
            # 買登録
            buy_pair = Symbol(to_currency = symbol.get('baseAsset'), from_currency = symbol.get('quoteAsset'), symbol = symbol.get('symbol'), side = SIDE_BUY)
            buy_pair.save()

            # 売登録
            sell_pair = Symbol(to_currency = symbol.get('quoteAsset'), from_currency = symbol.get('baseAsset'), symbol = symbol.get('symbol'), side = SIDE_SELL)
            sell_pair.save()

        qs = Symbol.get_scenario_patterns(client)
        for order_seq in qs:
            sym1 = Symbol.objects.get(id = order_seq.t1_id)
            sym2 = Symbol.objects.get(id = order_seq.t2_id)
            sym3 = Symbol.objects.get(id = order_seq.t3_id)
            new_seq = OrderSequence(t1 = sym1, t2 = sym2, t3 = sym3)
            new_seq.save()
        logger.info('END')
     
        