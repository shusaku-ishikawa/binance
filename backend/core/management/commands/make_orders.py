import logging
import os
from django.utils import timezone
from django.core.management.base import BaseCommand
from core.models import *
from binance.client import Client
from api.modules.helpers import _get_order_patterns, floating_decimals, round_by_step, _get_expected_scenario, _execute_scenario
from binance.enums import *
import time, logging
class Command(BaseCommand):
    help = '注文を発行する'
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        logger = logging.getLogger('batch')
        for user in User.objects.filter(is_active = True, api_key__isnull = False, api_secret_key__isnull = False):
            client = Client(user.api_key, user.api_secret_key)
            for os in OrderSequence.objects.filter(t1__from_currency = user.currency):
                # ユーザが自動取引をONにしている場合のみ処理
                user.refresh_from_db()
                if not user.auto_trading:
                    continue
                
                try:
                    scenario = _get_expected_scenario(client, os)
                except Exception as e:
                    logger.error(str(e))
                    continue
                else:
                    if not scenario.get('is_valid'):
                        continue
                    else:
                        try:
                            result = _execute_scenario(user, client, scenario, os)
                        except Exception as e:
                            logger.error('{msg}'.format(msg = str(e)))
                        else:
                            logger.info('[DONE]id:{osr_id} profit:{profit}'.format(osr_id = result.id, profit = result.profit))