import logging
import os
from django.utils import timezone
from django.core.management.base import BaseCommand
from core.models import *
from binance.client import Client
from binance.enums import *
import time
class Command(BaseCommand):
    help = 'アカウント情報を確認する'
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        logger = logging.getLogger('batch')
        logger.info('START')
        
        time_started = time.time()
        n = 0
        while True:
            time.sleep(3)
            n = n + 1
            time_elapsed = time.time() - time_started
            if time_elapsed > 55.0:
                break
        
            for sr in OrderSequenceResult.objects.all():
                
                if not sr.in_progress:
                    continue
                o1 = sr.t1_result
                o2 = sr.t2_result
                o3 = sr.t3_result


                if not o1.status:
                    o1.place()
                    continue
                elif o1.is_open:
                    o1.update_status()
                    if o1.status == ORDER_STATUS_FILLED:
                        o2.place()
                    continue
                elif o1.status == ORDER_STATUS_CANCELED:
                    o2.cancel()
                    o3.cancel()
                    continue
                elif o1.status == ORDER_STATUS_FILLED:
                    pass
            
                
                if not o2.status:
                    o2.place()
                    continue
                if o2.is_open:
                    o2.update_status()
                    if o2.status == ORDER_STATUS_FILLED:
                        o3.place()
                    continue
                elif o2.status == ORDER_STATUS_FILLED:
                    pass
                
            
                if not o3.status:
                    o3.place()
                    continue
                elif o3.is_open:
                    
                    o3.update_status()
                elif o3.status == ORDER_STATUS_FILLED:
                    pass

        logger.info('˜END')
