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

    def _get_order_patterns(self, client, currency = None):
        sql = ''
        sql += 'select'
        sql += '    t1.id as id,'
        sql += '    t1.id as t1_id, '
        sql += '    t2.id as t2_id, '
        sql += '    t3.id as t3_id '
        sql += 'from core_symbol as t1 '
        sql += 'inner join core_symbol as t2 '
        sql += '    on t1.to_currency = t2.from_currency '
        sql += 'inner join core_symbol as t3 '
        sql += '    on t2.to_currency = t3.from_currency '
        sql += 'where t1.from_currency = t3.to_currency '
        if currency:
            sql += "and t1.from_currency = '{currency}';".format(currency = currency)
        return Symbol.objects.raw(sql)

    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        # symbol全て削除
        Symbol.objects.all().delete()
        api_key = '17ckzmZUmU7jglRfmESIgDtE7a5TrfEB4Wz64h5oZ9Mi4bG1mvoJC2dtPQYeZYMf'
        api_secret_key = 'k21zTLm0aBAMokpawmvWtMlEOE9B87o7o6GXfUFlbOfD3Dx48TBgq5xz4e1vBG6H'
        client = Client(api_key, api_secret_key)
        info = client.get_exchange_info()
        symbols = info.get('symbols')
        for symbol in symbols:
            # 買登録
            buy_pair = Symbol(to_currency = symbol.get('baseAsset'), from_currency = symbol.get('quoteAsset'), symbol = symbol.get('symbol'), side = SIDE_BUY)
            buy_pair.save()

            # 売登録
            sell_pair = Symbol(to_currency = symbol.get('quoteAsset'), from_currency = symbol.get('baseAsset'), symbol = symbol.get('symbol'), side = SIDE_SELL)
            sell_pair.save()

        qs = self._get_order_patterns(client)
        for order_seq in qs:
            sym1 = Symbol.objects.get(id = order_seq.t1_id)
            sym2 = Symbol.objects.get(id = order_seq.t2_id)
            sym3 = Symbol.objects.get(id = order_seq.t3_id)
            new_seq = OrderSequence(t1 = sym1, t2 = sym2, t3 = sym3)
            new_seq.save()
        