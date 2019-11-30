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
        logger.info('START')
        time_started = time.time()
        while True:
            time.sleep(3)
            time_elapsed = time.time() - time_started
            if time_elapsed > 60 * 50:# 50分間継続する
                break

            for user in User.objects.filter(is_active = True, api_key__isnull = False, api_secret_key__isnull = False):
                if not user.auto_trading:
                    continue
                if user.active_scenario_count >= user.max_active_scenario:
                    logger.info('Max active scenario exceeded {}'.format(user.email))
                    continue
                for os in OrderSequence.objects.filter(t1__from_currency__in = user.base_currencies):
                    logger.info('try {}..'.format(os.transition))
                    time.sleep(2)
                    # ユーザが自動取引をONにしている場合のみ処理
                    user.refresh_from_db()
                    
                    scenario = Scenario(os, user)
                    scenario.estimate()
                    if not scenario.is_valid:
                        logger.error(scenario.error_message)
                        continue
                    
                    if scenario.profit_rate < user.target_profit_rate:
                        continue
                    logger.info('Found profitable scenario:{transition}. profit rate:{rate}%'.format(transition = os.transition, rate = scenario.profit_rate))
                    scenario.execute()
                    if not scenario.is_valid:
                        logger.error(scenario.error_message)
                        continue
                    result = scenario.result
                    logger.info('[DONE]id:{osr_id} profit:{profit}'.format(osr_id = result.id, profit = result.profit))

        logger.info('END')
