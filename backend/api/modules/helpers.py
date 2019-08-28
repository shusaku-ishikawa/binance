from core.models import *
import math
from binance.enums import *
from time import sleep

def round_by_step(a, MinClip):
    return math.floor(float(a) / MinClip) * MinClip

def floating_decimals(f_val, dec):
    prc = "{:."+str(dec)+"f}" #first cast decimal as str
    return prc.format(f_val)

'''
    全てのパターンを取得する
'''
def _get_order_patterns(client, currency = None):
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

'''
    相場を取得
'''
def _get_ticker(client, symbol):
    result = client.get_ticker(symbol = symbol.symbol)
    # 売りの場合
    if symbol.side == SIDE_SELL:
        price = result.get('bidPrice')
    else:
        price = result.get('askPrice')
    return float(price)

'''
    最安値から２番目の板情報を取得する
'''
def _get_2nd_entry(client, symbol):
    result = client.get_order_book(symbol = symbol.symbol)
    entry_array = result.get('asks' if symbol.side == SIDE_SELL else 'bids')
    if len(entry_array) == 0:
        raise Exception('板に取引がありません')
    elif len(entry_array) == 1:
        target_index = len(entry_array) - 1
    else:
        target_index = len(entry_array) -2
    return [float(o) for o in entry_array[target_index]]  

def _get_order_amount(client, orderseq):

    t1_target_entry = _get_2nd_entry(client, orderseq.t1)
    t1_rate = _get_ticker(client, orderseq.t1)

    t2_target_entry = _get_2nd_entry(client, orderseq.t2)
    t2_rate = _get_ticker(client, orderseq.t2)
    
    t3_target_entry = _get_2nd_entry(client, orderseq.t3)
    t3_rate = _get_ticker(client, orderseq.t3)
    
    ## A → B → C → Aとする
    t1_A_amount = t1_target_entry[1] if orderseq.t1.is_sell else (t1_target_entry[1] * t1_rate)
    t2_B_amount = t2_target_entry[1] if orderseq.t2.is_sell else (t2_target_entry[1] * t2_rate)
    t2_A_amount = (t2_B_amount / t1_rate) if orderseq.t1.is_sell else (t2_B_amount * t1_rate)
    t3_A_amount = (t3_target_entry[1] * t3_rate) if orderseq.t3.is_sell else t3_target_entry[1]
    
    A_order_amount = 0

    if t1_A_amount >= t2_A_amount:
        if t2_A_amount >= t3_A_amount:
            A_order_amount = t3_A_amount
        else:
            A_order_amount = t2_A_amount
    else:
        if t1_A_amount >= t3_A_amount:
            A_order_amount = t3_A_amount
        else:
            A_order_amount = t1_A_amount
    
    return A_order_amount

def _validate_amount(symbol_info, side, rate, amount):
    min_amount = float([f for f in symbol_info.get('filters') if f.get('filterType') == 'MIN_NOTIONAL'][0].get('minNotional'))
    cost = amount if side == SIDE_SELL else amount * rate
    return cost >= min_amount

def _get_valid_amount(symbol_info, amount):
    precision = symbol_info.get('baseAssetPrecision')
    step = float([f for f in symbol_info.get('filters') if f.get('filterType') == 'LOT_SIZE'][0].get('stepSize'))
    return round_by_step(floating_decimals(amount, precision), step)
    
def _get_expected_scenario(client, orderseq):
    ret = {
        'is_valid': True
    }

    t1_price = _get_2nd_entry(client, orderseq.t1)[0]
    t2_price = _get_2nd_entry(client, orderseq.t2)[0]
    t3_price = _get_2nd_entry(client, orderseq.t3)[0]


    ''' t1 取引 '''
    start_amount = _get_order_amount(client, orderseq)
    
    ## テスと目的のため0.001に固定
    start_amount = 0.001

    # 現在の所有分を確認
    balance = float(client.get_asset_balance(asset = orderseq.t1.from_currency).get('free'))
    if start_amount > balance:
        message = '注文しようとする数量を持ち合わせておりません: 期待={start_amount}, 所有={free}'.format(start_amount = start_amount, free = balance)
        print(message)
        ret['is_valid'] = False
        ret['message'] = message
        return ret

    t1_amount_temp = start_amount if orderseq.t1.is_sell else (start_amount / t1_price)
    t1_symbol_info = client.get_symbol_info(symbol = orderseq.t1.symbol)
    t1_amount = _get_valid_amount(t1_symbol_info, t1_amount_temp)
    # 注文数量が正しいかどうか確認
    if not _validate_amount(t1_symbol_info, orderseq.t1.side, t1_price, t1_amount):
        message = 't1の注文数量が不正です'
        ret['is_valid'] = False
        ret['message'] = message
        return ret

    # t1により取得される通貨B
    b_acquired = (t1_amount * t1_price) if orderseq.t1.is_sell else t1_amount
    b_acquired = b_acquired * 0.99
    t1_info = {
        'symbol': orderseq.t1.symbol,
        'quantity': t1_amount,
        'rate': t1_price,
        'side': orderseq.t1.side,
        'currency_acquired': orderseq.t1.to_currency,
        'quote_quantity': b_acquired,
        'symbol_info': t1_symbol_info
    }
    ret['t1_info'] = t1_info

    ''' t2 取引 '''
    t2_symbol_info = client.get_symbol_info(symbol = orderseq.t2.symbol)
    t2_amount_temp = b_acquired if orderseq.t2.is_sell else (b_acquired / t2_price)
    t2_amount = _get_valid_amount(t2_symbol_info, t2_amount_temp)
    # 注文数量が正しいかどうか確認
    if not _validate_amount(t2_symbol_info, orderseq.t2.side, t2_price, t2_amount):
        message = 't2の注文数量が不正です'
        print(message)
        ret['is_valid'] = False
        ret['message'] = message
        return ret

    c_acquired = (t2_amount * t2_price) if orderseq.t2.is_sell else t2_amount
    c_acquired = c_acquired * 0.99
    t2_info = {
        'symbol': orderseq.t2.symbol,
        'quantity': t2_amount,
        'rate': t2_price,
        'side': orderseq.t2.side,
        'currency_acquired': orderseq.t2.to_currency,
        'quote_quantity': c_acquired,
        'symbol_info': t2_symbol_info
    }
    ret['t2_info'] = t2_info

    ''' t3取引 '''
    t3_symbol_info = client.get_symbol_info(symbol = orderseq.t3.symbol)
    t3_amount_temp = c_acquired if orderseq.t3.is_sell else (c_acquired / t3_price)
    t3_amount = _get_valid_amount(t3_symbol_info, t3_amount_temp)
    # 注文数量が正しいかどうか確認
    if not _validate_amount(t3_symbol_info, orderseq.t3.side, t3_price, t3_amount):
        message = 't3の注文数量が不正です'
        ret['is_valid'] = False
        ret['message'] = message
        return ret
    a_acquired_ret = (c_acquired * t3_price) if orderseq.t3.is_sell else (c_acquired / t3_price)
    a_acquired_ret = a_acquired_ret * 0.99
    t3_info = {
        'symbol': orderseq.t3.symbol,
        'quantity': t3_amount,
        'rate': t3_price,
        'side': orderseq.t3.side,
        'currency_acquired': orderseq.t3.to_currency,
        'quote_quantity': a_acquired_ret,
        'symbol_info': t3_symbol_info
    }
    ret['t3_info'] = t3_info
    ret['profit'] = floating_decimals(a_acquired_ret - start_amount, 8)
    return ret

def _execute_scenario(user, client, scenario, orderseq):
    t1_info = scenario.get('t1_info')
    try:
        if t1_info.get('side') == SIDE_SELL:
            t1 = client.order_market_sell(
                symbol=t1_info.get('symbol'),
                quantity=t1_info.get('quantity')
            )
        else:
            t1 = client.order_market_buy(
                symbol=t1_info.get('symbol'),
                quantity=t1_info.get('quantity')
            )
    except Exception as e:
        raise Exception('t1-{symbol}/{side} 注文が失敗しました:{msg}'.format(symbol = t1_info.get('symbol'), side = t1_info.get('side'),msg = str(e) ))
    else:
        t1_order_id = t1.get('orderId')
        
        # ステータスの監視
        while True:
            order_info = client.get_order(
                symbol=t1_info.get('symbol'),
                orderId=t1_order_id
            )
            status = order_info.get('status')
            if status == ORDER_STATUS_FILLED:
                # 約定した場合注文履歴を作成
                t1_order_result = Order()
                t1_order_result.user = user
                t1_order_result.symbol = orderseq.t1
                t1_order_result.order_id = order_info.get('orderId')
                t1_order_result.quantity = float(order_info.get('executedQty'))
                t1_order_result.quote_quantity = float(order_info.get('cummulativeQuoteQty'))
                t1_order_result.expected_rate = t1_info.get('rate')
                t1_order_result.time = order_info.get('time') / 1000
                t1_order_result.save()
                initial_cost = float(order_info.get('quantity')) if t1_info.get('side') == SIDE_SELL else float(order_info.get('cummulativeQuoteQty'))
                break
            # 注文が拒否もしくは期限切れした場合
            elif status in { ORDER_STATUS_REJECTED, ORDER_STATUS_EXPIRED }:
                raise Exception('注文が拒否されました')
            else:
                pass
            sleep(1)
        
    # t2実行
    t2_info = scenario.get('t2_info')

    try:
        if t2_info.get('side') == SIDE_SELL:
            t2 = client.order_market_sell(
                symbol=t2_info.get('symbol'),
                quantity=t2_info.get('quantity')
            )
        else:
            t2 = client.order_market_buy(
                symbol=t2_info.get('symbol'),
                quantity=t2_info.get('quantity')
            )
    except Exception as e:
        raise Exception('t2-{symbol}/{side} 注文が失敗しました:{msg}'.format(symbol = t2_info.get('symbol'), side = t2_info.get('side'),msg = str(e) ))
    
    else:
        t2_order_id = t2.get('orderId')
        # ステータスの監視
        while True:
            order_info = client.get_order(
                symbol=t2_info.get('symbol'),
                orderId=t2_order_id
            )
            print(order_info)
            status = order_info.get('status')
            if status == ORDER_STATUS_FILLED:
                # 約定した場合注文履歴を作成
                t2_order_result = Order()
                t2_order_result.user = user
                t2_order_result.symbol = orderseq.t2
                t2_order_result.order_id = order_info.get('orderId')
                t2_order_result.quantity = float(order_info.get('executedQty'))
                t2_order_result.quote_quantity = float(order_info.get('cummulativeQuoteQty'))
                t2_order_result.expected_rate = t2_info.get('rate')
                t2_order_result.time = order_info.get('time') / 1000
                t2_order_result.save()
                break
            # 注文が拒否もしくは期限切れした場合
            elif status in { ORDER_STATUS_REJECTED, ORDER_STATUS_EXPIRED }:
                raise Exception('注文が拒否されました')
            else:
                pass
            sleep(1)    
    # t3実行
    t3_info = scenario.get('t3_info')
    try:
        if t3_info.get('side') == SIDE_SELL:
            t3 = client.order_market_sell(
                symbol=t3_info.get('symbol'),
                quantity=t3_info.get('quantity')
            )
        else:
            t3 = client.order_market_buy(
                symbol=t3_info.get('symbol'),
                quantity=t3_info.get('quantity')
            )
    except Exception as e:
        raise Exception('t3-{symbol}/{side} 注文が失敗しました:{msg}'.format(symbol = t3_info.get('symbol'), side = t3_info.get('side'),msg = str(e) ))
    
    else:
        t3_order_id = t3.get('orderId')
        # ステータスの監視
        while True:
            order_info = client.get_order(
                symbol=t3_info.get('symbol'),
                orderId=t3_order_id
            )
            print(order_info)
            status = order_info.get('status')
            if status == ORDER_STATUS_FILLED:
                # 約定した場合注文履歴を作成
                t3_order_result = Order()
                t3_order_result.user = user
                t3_order_result.symbol = orderseq.t3
                t3_order_result.order_id = order_info.get('orderId')
                t3_order_result.quantity = float(order_info.get('executedQty'))
                t3_order_result.quote_quantity = float(order_info.get('cummulativeQuoteQty'))
                t3_order_result.expected_rate = t3_info.get('rate')
                t3_order_result.time = order_info.get('time') / 1000
                t3_order_result.save()
                last_profit = float(order_info.get('quantity')) if t3_info.get('side') == SIDE_BUY else float(order_info.get('cummulativeQuoteQty'))
                break
            # 注文が拒否もしくは期限切れした場合
            elif status in { ORDER_STATUS_REJECTED, ORDER_STATUS_EXPIRED }:
                raise Exception('注文が拒否されました')
            else:
                pass
            sleep(1)    
    # OrderSequenceResult作成
    osr = OrderSequenceResult()
    osr.user = user
    osr.master = orderseq
    osr.t1_result = t1_order_result
    osr.t2_result = t2_order_result
    osr.t3_result = t3_order_result
    osr.expected_profit = scenario.get('profit')
    osr.profit = floating_decimals(last_profit - initial_cost, 8)
    osr.save()
    return osr