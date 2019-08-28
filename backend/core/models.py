from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from datetime import datetime
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from binance.enums import *
from unixtimestampfield.fields import UnixTimeStampField

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

    auto_trading = models.BooleanField(
        verbose_name = '自動取引',
        default = False
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
 

    @property
    def username(self):
        """username属性のゲッター

        他アプリケーションが、username属性にアクセスした場合に備えて定義
        メールアドレスを返す
        """
        return self.email

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
        verbose_name = 'orderId'
    )
    quantity = models.FloatField(
        verbose_name = 'base_数量',
    )
    quote_quantity = models.FloatField(
        verbose_name = 'quote_数量'
    )
    expected_rate = models.FloatField(
        verbose_name = '期待していたレート'
    )
    time = UnixTimeStampField(default=0.0)
    
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
    expected_profit = models.FloatField(
        verbose_name = '想定利益'
    )
    profit = models.FloatField(
        verbose_name = '利益'
    )
    @property
    def time(self):
        return t3_result.time
    

    
    
