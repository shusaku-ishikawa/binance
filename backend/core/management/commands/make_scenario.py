import logging
import os
from django.utils import timezone
from django.core.management.base import BaseCommand
from core.models import *
from binance.enums import *
import time, logging
class Command(BaseCommand):
    help = '注文を発行する'
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        logger = logging.getLogger('batch')
        logger.info('開始')
        time_started = time.time()
        n = 0
        while True:
            time.sleep(1)
            n = n + 1
            time_elapsed = time.time() - time_started
            if time_elapsed > 55.0:
                break
        
            for user in User.objects.filter(is_active = True, api_key__isnull = False, api_secret_key__isnull = False):
                if not user.auto_trading:
                    continue
                for os in OrderSequence.objects.filter(t1__from_currency = user.currency):
                    time.sleep(1)
                    # ユーザが自動取引をONにしている場合のみ処理
                    user.refresh_from_db()
                    if user.active_scenario_count >= user.max_active_scenario:
                        continue
                    
                    scenario = Scenario(os, user)
                    scenario.estimate()
                    if not scenario.is_valid:
                        logger.error(scenario.error_message)
                        continue
                    
                    if scenario.profit < user.target_profit_rate:
                        continue
                    
                    scenario.execute()
                    if not scenario.is_valid:
                        logger.error(scenario.error_message)
                        continue
                    result = scenario.result
                    logger.info('[DONE]id:{osr_id} profit:{profit}'.format(osr_id = result.id, profit = result.profit))