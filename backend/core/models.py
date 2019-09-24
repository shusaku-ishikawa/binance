from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from datetime import datetime
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from binance.enums import *
from binance.client import Client
from unixtimestampfield.fields import UnixTimeStampField
import math, time
class UserManager(BaseUserManager):
    """ユーザーマネージャー."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """メールアドレスでの登録を必須にする"""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """is_staff(管理サイトにログインできるか)と、is_superuer(全ての権限)をFalseに"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """スーパーユーザーは、is_staffとis_superuserをTrueに"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
        
    email = models.EmailField(_('メールアドレス'), unique=True)
    api_key = models.CharField(_('API KEY'), max_length=255, blank=True, null = True)
    api_secret_key = models.CharField(_('API SECRET KEY'), max_length=255, blank=True, null = True)
    currency = models.CharField(
        verbose_name = 'ターゲット通貨',
        max_length = 50,
    )
    
    max_quantity_rate = models.FloatField(
        verbose_name = '取引上限%',
        default = 0.5
    )

    target_profit_rate = models.FloatField(
        verbose_name = '取引施行利益',
        default = 0.5
    )

    transaction_fee_rate = models.FloatField(
        verbose_name = '取引手数料',
        default = 0.075
    )
    auto_trading = models.BooleanField(
        verbose_name = '自動取引',
        default = False
    )
    max_active_scenario = models.IntegerField(
        verbose_name = '最大シナリオ数',
        default = 10
    )
    scenario_unit = models.FloatField(
        verbose_name = 'unit',
        default = 0.2
    )
    is_staff = models.BooleanField(
        _('管理者'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('利用開始'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
 
    def get_binance_client(self):
        return Client(self.api_key, self.api_secret_key)
    @property
    def username(self):
        """username属性のゲッター

        他アプリケーションが、username属性にアクセスした場合に備えて定義
        メールアドレスを返す
        """
        return self.email
    @property
    def active_scenario_count(self):
        return len(OrderSequenceResult.objects.filter(user__id = self.id))


'''
    取引可能な通貨ペアのマスタ情報
'''
class Symbol(models.Model):
    class Meta:
        verbose_name = 'シンボル'
        verbose_name_plural = 'シンボル'

    def __str__(self):
        return '{symbol} {side}'.format(symbol = self.symbol, side = self.side)
    
    symbol = models.CharField(
        verbose_name = '通貨',
        max_length = 20
    )
    
    from_currency = models.CharField(
        verbose_name = '元通貨',
        max_length = 10
    )
    to_currency = models.CharField(
        verbose_name = '取得通貨',
        max_length = 10
    )
    
    side = models.CharField(
        verbose_name = 'サイド',
        max_length = 10
    )
    @property
    def is_sell(self):
        return self.side == SIDE_SELL
    def get_ticker(self):
        result = Client().get_ticker(symbol = self.symbol)
        # 売りの場合
        if self.side == SIDE_SELL:
            price = result.get('bidPrice')
        else:
            price = result.get('askPrice')
        return float(price)
class OrderSequence(models.Model):
    class Meta:
        verbose_name = '注文シナリオ'
        verbose_name_plural = '注文シナリオ'

    def __str__(self):
        return '{t1_symbol} - {t2_symbol} - {t3_symbol}'.format(t1_symbol = self.t1_symbol, t2_symbol = self.t2_symbol, t3_symbol = self.t3_symbol)
   
    t1 = models.ForeignKey(
        to = Symbol,
        verbose_name = 't1',
        related_name = 'myseq_t1',
        on_delete = models.CASCADE
    )
    t2 = models.ForeignKey(
        to = Symbol,
        verbose_name = 't2',
        related_name = 'myseq_t2',
        on_delete = models.CASCADE
    )
    t3 = models.ForeignKey(
        to = Symbol,
        verbose_name = 't3',
        related_name = 'myseq_t3',
        on_delete = models.CASCADE
    )
    @property
    def t1_symbol(self):
        return self.t1.symbol
    @property
    def t2_symbol(self):
        return self.t2.symbol
    @property
    def t3_symbol(self):
        return self.t3.symbol
    @property
    def t1_side(self):
        return self.t1.side
    @property
    def t2_side(self):
        return self.t2.side
    @property
    def t3_side(self):
        return self.t3.side
    @property
    def transition(self):
        return '{c1}-{c2}-{c3}-{c4}'.format(c1 = self.t1.from_currency, c2 = self.t1.to_currency, c3 = self.t2.to_currency, c4 = self.t3.to_currency)


class Order(models.Model):
    class Meta:
        verbose_name = '注文'
        verbose_name_plural = '注文'
    def __str__(self):
        return str(self.order_id)

    user = models.ForeignKey(
        to = User,
        verbose_name = 'ユーザ',
        on_delete = models.CASCADE
    )
    symbol = models.ForeignKey(
        to = Symbol,
        verbose_name = 'シンボル',
        on_delete = models.CASCADE
    )
    order_id = models.IntegerField(
        verbose_name = 'orderId',
        null = True
    )
    quantity = models.FloatField(
        verbose_name = 'base_数量'
    )
    price = models.FloatField(
        verbose_name = '価格'
    )
    time = UnixTimeStampField(default=0.0)
    
    status = models.CharField(
        verbose_name = 'ステータス',
        max_length = 100,
        null = True
    )
    error_message = models.CharField(
        verbose_name = 'エラーメッセージ',
        null = True,
        blank = True,
        max_length = 100
    )
    @property
    def quote_quantity(self):
        return self.quantity * self.price

    @property
    def safe_price(self):
        from decimal import Decimal, ROUND_DOWN
        return "{0:.8f}".format(Decimal(self.price))
        

    @property
    def is_open(self):
        return self.status in { ORDER_STATUS_NEW, ORDER_STATUS_PARTIALLY_FILLED }
    @property
    def currecy_acquired(self):
        return self.symbol.to_currency

    @property
    def amount_acquired(self):
        if self.side == SIDE_SELL:
            return (self.quote_quantity or 0) * (1 - self.user.transaction_fee_rate / 100)
        else:
            return  self.quantity * (1 - self.user.transaction_fee_rate / 100)

    @property
    def currency_paid(self):
        return self.symbol.from_currency

    @property
    def amount_paid(self):
        if self.side == SIDE_SELL:
            return self.quantity
        else:
            return (self.quote_quantity or 0)
    
    @property
    def actual_rate(self):
        val = self.quote_quantity / self.quantity
        prc = "{:."+str(8)+"f}" #first cast decimal as str
        return prc.format(val)

    @property
    def str_symbol(self):
        return self.symbol.symbol
    
    @property
    def side(self):
        return self.symbol.side

    def place(self):
        client = self.user.get_binance_client()
        try:
            if self.side == SIDE_SELL:
                result = client.order_limit_sell(
                    symbol=self.str_symbol,
                    quantity=self.quantity,
                    price=self.safe_price
                )
            else:
                result = client.order_limit_buy(
                    symbol=self.str_symbol,
                    quantity=self.quantity,
                    price=self.safe_price
                )
        except Exception as e:
            print('{symbol}/qty:{quantity}/price:{price}の注文に失敗:{err}'.format(symbol = self.str_symbol, quantity = self.quatity, price = self.safe_price, err =str(e)))
        
        else:
            print(result)
            self.order_id = result.get('orderId')
            self.time = result.get('transactTime') / 1000
            self.status = result.get('status')
            self.save()
    def cancel(self):
        if not self.status:
            self.status = ORDER_STATUS_CANCELED
        client = self.user.get_binance_client()
        try:
            result = client.cancel_order(
                symbol=self.str_symbol,
                orderId=self.order_id
            )
        except Exception as e:
            print('{order_id}のキャンセルに失敗:{err}'.format(order_id = self.order_id, err =str(e)))
        else:
            self.time = result.get('transactTime') / 1000
            self.status = result.get('status')
            self.save()

    def update_status(self):
        if not self.order_id:
            return False
        client = self.user.get_binance_client()
        try:
            result = client.get_order(
                symbol=self.str_symbol,
                orderId=self.order_id
            )
        except Exception as e:
            print('{order_id}の更新に失敗:{err}'.format(order_id = self.order_id, err = str(e)))
        else:
            self.status = result.get('status')
            self.save()   

class OrderSequenceResult(models.Model):
    class Meta:
        verbose_name = 'シナリオ実行結果'
        verbose_name_plural = 'シナリオ実行結果'
    
    def __str__(self):
        return '利益 : {}'.format(self.profit)

    user = models.ForeignKey(
        to = User,
        verbose_name = 'ユーザ',
        on_delete = models.CASCADE
    )
    master = models.ForeignKey(
        to = OrderSequence,
        on_delete = models.CASCADE
    )
    t1_result = models.ForeignKey(
        to = Order,
        on_delete = models.CASCADE,
        related_name = 'seq_t1'
    )
    t2_result = models.ForeignKey(
        to = Order,
        on_delete = models.CASCADE,
        related_name = 'seq_t2'
    )
    t3_result = models.ForeignKey(
        to = Order,
        on_delete = models.CASCADE,
        related_name = 'seq_t3'
    )

    @property
    def profit(self):
        if not self.t3_result.quote_quantity:
            return None
        return self.t3_result.amount_acquired - self.t1_result.amount_paid
    @property
    def time(self):
        return self.t3_result.time
    
    @property
    def in_progress(self):
        if self.t1_result.is_open or not self.t1_result.status:
            return True
        if self.t2_result.is_open or not self.t2_result.status:
            return True
        if self.t3_result.is_open or not self.t3_result.status:
            return True
        return False
    @property
    def is_completed(self):
        return (self.t1_result.status == ORDER_STATUS_FILLED) \
                and (self.t2_result.status == ORDER_STATUS_FILLED) \
                and (self.t3_result.status == ORDER_STATUS_FILLED)
    
class Scenario(object):
    def __init__(self, orderseq, user):
        self.user = user
        self.orderseq = orderseq
        self.client = self.user.get_binance_client()
        self.is_valid = True
        self.result = None

    def get_ita_price(self, symbol, num):
        result = self.client.get_order_book(symbol = symbol.symbol)
        entry_array = result.get('asks' if symbol.side == SIDE_SELL else 'bids')
        if len(entry_array) < num:
            self.is_valid = False
            self.error_message = '板に取引がありません'
        else:
            return [float(o) for o in entry_array[num - 1]]  
    
    def get_order_amount(self, t1_rate, t2_rate, t3_rate):
        pass
        # t1_target_entry = self.get_ita_price(self.orderseq.t1, 2)
        # t1_rate = orderseq.t1.get_ticker()

        # t2_target_entry = _get_2nd_entry(client, orderseq.t2)
        # t2_rate = orderseq.t2.get_ticker()
        
        # t3_target_entry = _get_2nd_entry(client, orderseq.t3)
        # t3_rate = orderseq.t3.get_ticker()
        
        # ## A → B → C → Aとする
        # t1_A_amount = t1_target_entry[1] if orderseq.t1.is_sell else (t1_target_entry[1] * t1_rate)
        # t2_B_amount = t2_target_entry[1] if orderseq.t2.is_sell else (t2_target_entry[1] * t2_rate)
        # t2_A_amount = (t2_B_amount / t1_rate) if orderseq.t1.is_sell else (t2_B_amount * t1_rate)
        # t3_A_amount = (t3_target_entry[1] * t3_rate) if orderseq.t3.is_sell else t3_target_entry[1]
        
        # A_order_amount = 0

        # if t1_A_amount >= t2_A_amount:
        #     if t2_A_amount >= t3_A_amount:
        #         A_order_amount = t3_A_amount
        #     else:
        #         A_order_amount = t2_A_amount
        # else:
        #     if t1_A_amount >= t3_A_amount:
        #         A_order_amount = t3_A_amount
        #     else:
        #         A_order_amount = t1_A_amount
        
        # return A_order_amount
    @staticmethod
    def round_by_step(a, MinClip):
        return math.floor(float(a) / MinClip) * MinClip
    @staticmethod
    def floating_decimals(amount, precision):
        # prc = "{:."+str(dec)+"f}" #first cast decimal as str
        # return prc.format(f_val)
        return float("{:0.0{}f}".format(amount, precision))
    @staticmethod
    def get_valid_amount(symbol_info, amount):
        precision = symbol_info.get('baseAssetPrecision')
        step = float([f for f in symbol_info.get('filters') if f.get('filterType') == 'LOT_SIZE'][0].get('stepSize'))
        return Scenario.floating_decimals(Scenario.round_by_step(amount, step), precision)
    @staticmethod
    def violate_min_notional(symbol_info, side, rate, amount):
        min_notional = float([f for f in symbol_info.get('filters') if f.get('filterType') == 'MIN_NOTIONAL'][0].get('minNotional'))
        notional = rate * amount
        if notional < min_notional:
            print('min notional:{mn}に対し{n}で発注しようとしています symbol:{symbol}, side:{side}, amount:{amount}, rate:{rate} '.format(mn = min_notional, n = notional, symbol = symbol_info.get('symbol'), side = side, amount = amount, rate = rate))
        return notional < min_notional


    def estimate(self):
        n = 1

        t1_price = self.get_ita_price(self.orderseq.t1, n)[0]
        t2_price = self.get_ita_price(self.orderseq.t2, n)[0]
        t3_price = self.get_ita_price(self.orderseq.t3, n)[0]
    
        ## テスと目的のため0.001に固定
        
        # 現在の所有分を確認
        balance = float(self.client.get_asset_balance(asset = self.orderseq.t1.from_currency).get('free'))
        unit = self.user.scenario_unit

        if unit > balance:
            self.is_valid = False
            self.error_message = '注文しようとする数量を持ち合わせておりません: 期待={unit}, 所有={free}'.format(unit = unit, free = balance)
            return None

        t1_amount_temp = unit if self.orderseq.t1.is_sell else (unit / t1_price)
        t1_symbol_info = self.client.get_symbol_info(symbol = self.orderseq.t1.symbol)
        t1_amount = Scenario.get_valid_amount(t1_symbol_info, t1_amount_temp)
        
        if self.orderseq.t1.is_sell:
            initial_cost = t1_amount
        else:
            initial_cost = t1_amount * t1_price
        
        # 注文数量が正しいかどうか確認
        if  Scenario.violate_min_notional(t1_symbol_info, self.orderseq.t1.side, t1_price, t1_amount):
            self.is_valid = False
            self.error_message = 't1の注文数量が不正です'
            return None

        b_acquired = (t1_amount * t1_price) if self.orderseq.t1.is_sell else t1_amount
        b_acquired = b_acquired * ((100 - self.user.transaction_fee_rate) / 100)
        
        self.t1_info = {
            'symbol': self.orderseq.t1.symbol,
            'quantity': t1_amount,
            'rate': t1_price,
            'side': self.orderseq.t1.side,
            'currency_acquired': self.orderseq.t1.to_currency,
            'amount_acquired': t1_amount * t1_price if self.orderseq.t1.is_sell else t1_amount,
            'symbol_info': t1_symbol_info
        }
        
        # t2 取引
        t2_symbol_info = self.client.get_symbol_info(symbol = self.orderseq.t2.symbol)
        t2_amount_temp = b_acquired if self.orderseq.t2.is_sell else (b_acquired / t2_price)
        t2_amount = Scenario.get_valid_amount(t2_symbol_info, t2_amount_temp)
        # 注文数量が正しいかどうか確認
        if Scenario.violate_min_notional(t2_symbol_info, self.orderseq.t2.side, t2_price, t2_amount):
            self.is_valid = False
            self.error_message = 't2の注文数量が不正です'
            return None
        c_acquired = (t2_amount * t2_price) if self.orderseq.t2.is_sell else t2_amount
        c_acquired = c_acquired * ((100 - self.user.transaction_fee_rate) / 100)
        
        self.t2_info = {
            'symbol': self.orderseq.t2.symbol,
            'quantity': t2_amount,
            'rate': t2_price,
            'side': self.orderseq.t2.side,
            'currency_acquired': self.orderseq.t2.to_currency,
            'amount_acquired': t2_amount * t2_price if self.orderseq.t2.is_sell else t2_amount,
            'symbol_info': t2_symbol_info
        }

        ''' t3取引 '''
        t3_symbol_info = self.client.get_symbol_info(symbol = self.orderseq.t3.symbol)
        t3_amount_temp = c_acquired if self.orderseq.t3.is_sell else (c_acquired / t3_price)
        t3_amount = Scenario.get_valid_amount(t3_symbol_info, t3_amount_temp)
        # 注文数量が正しいかどうか確認
        if Scenario.violate_min_notional(t3_symbol_info, self.orderseq.t3.side, t3_price, t3_amount):
            self.is_valid = False
            self.error_message = 't3の注文数量が不正です'
            return None

        a_acquired_ret = (c_acquired * t3_price) if self.orderseq.t3.is_sell else (c_acquired / t3_price)
        a_acquired_ret = a_acquired_ret * ((100 - self.user.transaction_fee_rate) / 100)
        self.t3_info = {
            'symbol': self.orderseq.t3.symbol,
            'quantity': t3_amount,
            'rate': t3_price,
            'side': self.orderseq.t3.side,
            'currency_acquired': self.orderseq.t3.to_currency,
            'amount_acquired': t3_amount * t3_price if self.orderseq.t3.is_sell else t3_amount,
            'symbol_info': t3_symbol_info
        }
        
        self.profit = Scenario.floating_decimals((a_acquired_ret - initial_cost) * 100 / initial_cost, 8)
    
    def execute(self):
        
        t1_obj = Order()
        t1_obj.user = self.user
        t1_obj.symbol = self.orderseq.t1
        t1_obj.quantity = self.t1_info.get('quantity')
        t1_obj.price = self.t1_info.get('rate')
        t1_obj.place()

        t1_obj.save()
        
        # 注文が拒否もしくは期限切れした場合
        if t1_obj.status in { ORDER_STATUS_REJECTED, ORDER_STATUS_EXPIRED }:
            self.is_valid = False
            self.error_message = '注文が失敗しました'
            return
        time.sleep(1)
            
        # t2実行
        t2_obj = Order()
        t2_obj.user = self.user
        t2_obj.symbol = self.orderseq.t2
        t2_obj.quantity = self.t2_info.get('quantity')
        t2_obj.price = self.t2_info.get('rate')
        t2_obj.save()

        t3_obj = Order()
        t3_obj.user = self.user
        t3_obj.symbol = self.orderseq.t3
        t3_obj.quantity = self.t3_info.get('quantity')
        t3_obj.price = self.t3_info.get('rate')
        t3_obj.save()

        osr = OrderSequenceResult()
        osr.user = self.user
        osr.master = self.orderseq
        osr.t1_result = t1_obj
        osr.t2_result = t2_obj
        osr.t3_result = t3_obj
        osr.save()
        self.result = osr