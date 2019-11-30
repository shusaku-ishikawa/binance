from rest_framework import serializers
from core.models import *

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'api_key', 'api_secret_key', 'do_btc', 'btc_unit_amount', 'do_eth', 'eth_unit_amount', 'do_usdt', 'usdt_unit_amount', 'do_bnb', 'bnb_unit_amount', 'max_quantity_rate', 'target_profit_rate', 'max_active_scenario', 'auto_trading')
        write_only_fields = ('password')
        read_only_fields = ('id',)

class OrderSequenceSerializer(serializers.HyperlinkedModelSerializer):
    t1_symbol = serializers.CharField()
    t2_symbol = serializers.CharField()
    t3_symbol = serializers.CharField()
    t1_side = serializers.CharField()
    t2_side = serializers.CharField()
    t3_side= serializers.CharField()
    transition = serializers.CharField()
    class Meta:
        model = OrderSequence
        fields = ('id', 't1_symbol', 't2_symbol', 't3_symbol', 't1_side', 't2_side', 't3_side', 'transition')

class SymbolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symbol
        fields = ('symbol', 'from_currency', 'to_currency', 'side')

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('order_id', 'str_symbol', 'side', 'quantity', 'quote_quantity', 'price', 'time', 'status', 'error_message')

class BinanceAPIDeserializer(serializers.Serializer):
    pass
class OrderSequenceResultSerializer(serializers.ModelSerializer):
    master = OrderSequenceSerializer(many = False, required = True)
    t1_result = OrderSerializer(many = False, required = True)
    t2_result = OrderSerializer(many = False, required = True)
    t3_result = OrderSerializer(many = False, required = True)
    class Meta:
        model = OrderSequenceResult
        fields = ('id', 'master', 't1_result', 't2_result', 't3_result', 'profit', 'is_completed')

class BalanceSerializer(serializers.Serializer):
    asset = serializers.CharField(max_length=200)
    free = serializers.FloatField()
    locked = serializers.FloatField()

class ScenarioDetailSerializer(serializers.Serializer):
    symbol = serializers.CharField()
    quantity = serializers.FloatField()
    rate = serializers.FloatField()
    side = serializers.CharField()
    currency_acquired = serializers.CharField()
    amount_acquired = serializers.FloatField()

class ScenarioSerializer(serializers.Serializer):
    orderseq = OrderSequenceSerializer(many = False, required = True)
    is_valid = serializers.BooleanField()
    t1_info = ScenarioDetailSerializer(many = False, required = True)
    t2_info = ScenarioDetailSerializer(many = False, required = True)
    t3_info = ScenarioDetailSerializer(many = False, required = True)
    profit = serializers.FloatField()
    profit_rate = serializers.FloatField()
