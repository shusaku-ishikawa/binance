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
        n = 0
        for user in User.objects.filter(is_active = True):
            client = user.get_binance_client()
            if not client:
                continue
            
            rate = int(client.get_account().get('makerCommission')) / 1000
            user.commission_rate = rate
            user.save()
            
        logger.info('END')
