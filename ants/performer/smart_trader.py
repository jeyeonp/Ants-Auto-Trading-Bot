# -*- coding: utf-8 -*-
import logging
from exchangem.exchanges.upbit import Upbit
from exchangem.model.observers import Observer

class SmartTrader:
    """
    config 
      - 트레이딩에 사용할 금액. 없으면 거래소에서 사용가능한 금액으로 사용한다
    
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.exchanges = {}
        pass
    
    def config(self):
        self.configs = {
            'upbit':{
                'krw_limit': 10000,
                'btc_limit': 1
            },
            'bithumb':{
                'krw_limit': 10000
            },
            'binance':{
                'btc_limit': 0.5,
                'usdt_limit': 10
            }
        }
        pass
    
    def add_exchange(self, name, exchange):
        self.exchanges[name] = exchange
    
    def trading(self, exchange_name, market, action, coin_name, price=None, count=None):
        """
        사용가능한 금액에 맞춰서 개수를 구매한다
        """
        exchange = self.exchanges.get(exchange_name)
        if(exchange == None):
            return None
        self.logger.debug('select exchange : {}'.format(exchange))
        
        symbol = coin_name + '/' + market #'BTC/KRW'
        if(not exchange.has_market(symbol)):
            self.logger.warning('{} has not market : {}'.format(exchange, market))
            return None

        seed_money = self.availabel_seed_money(exchange, market)  
        if(action == 'BUY'):
            ret = self._buy(exchange, market, coin_name, seed_money, price)
        elif(action == 'SELL'):
            ret = self._sell(exchange, market, coin_name, price, count)
            
        if(ret is None):
            self.logger.warning('action fail')
            return None
        
        return ret

    def _buy(self, exchange, market, coin_name, seed_size, price):
        symbol = coin_name + '/' + market #'BTC/KRW'
        _type = 'limit'  # or 'market' or 'limit'
        side = 'buy'  # 'buy' or 'sell'
        amount = 0
        
        if(price == None):
            price = exchange.get_last_price(symbol)
        amount, price, fee = exchange.check_amount(symbol, seed_size, price)
        params = {}
        desc = None
        
        self.logger.debug('_buy - price: {}, amount: {}, fee: {}'.format(price, amount, fee))
        try:
            desc = exchange.create_order(symbol, _type, side, amount, price, params)
            self.logger.debug('order complete : {}'.format(desc))
        except Exception as exp:
            self.logger.warning('create_order exception : {}'.format(exp))
            
        return desc
    
    def _sell(self, exchange, market, coin_name, seed_size, price):
        symbol = coin_name + '/' + market #'BTC/KRW'
        _type = 'limit'  # or 'market' or 'limit'
        side = 'sell'  # 'buy' or 'sell'
        amount = 0
        
        if(price == None):
            price = exchange.get_last_price(symbol)
        amount, price, fee = exchange.check_amount(symbol, seed_size, price)
        params = {}
        desc = None
        
        self.logger.debug('_buy - price: {}, amount: {}, fee: {}'.format(price, amount, fee))
        try:
            desc = exchange.create_order(symbol, _type, side, amount, price, params)
            self.logger.debug('order complete : {}'.format(desc))
        except Exception as exp:
            self.logger.warning('create_order exception : {}'.format(exp))
            
        return desc
        
    def availabel_seed_money(self, exchange, base):
        """
        사용 가능한 market base seed를 돌려준다
        1. config에서 설정된 값
        2. exchange별 설정된 값
        3. exchange에 가용 가능한 모든 머니
        """
        print(base)
        sm = exchange.get_limit(base)
        self.logger.debug('seed_money : {}'.format(sm))
        return sm
    
    def trading_limit(self, exchange, action, count, price):
        """
        fee만 계산해서 지정된 가격에 맞게 매매한다
        """
        pass
    
    
if __name__ == '__main__':
    print('SmartTrader test')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(formatter)
    logger.addHandler(stream_hander)
    
    