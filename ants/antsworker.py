import sys
import signal
import time
from pybithumb import Bithumb

import utils
import email_reader as email

M = None
bithumb = None

def signal_handler(sig, frame):
    print('\nExit Program by user Ctrl + C')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def init():
    keys = utils.readKey('./configs/bithumb.key')
    apiKey = keys['api_key']
    apiSecret = keys['api_secret']

    try:
        global bithumb
        bithumb = Bithumb(apiKey, apiSecret)
        M = email.conn()
        ret = email.login(M)
        email.logout(M)
    except Exception as exp:
        print(exp)
        sys.exit(1)
    
    
def start():
    M = email.conn()
    ret = email.login(M)
    if ret != 'OK' :
        print(ret)
        sys.exit(1)
    
    while(True):
        email.openFolder(M)
        time.sleep(5)  #입력값은 초단위이다. 10초마다 업데이트 확인함
        mthList = email.mailSearch(M)
        msgList = email.getMailList(M, mthList)
        
        for msg in msgList:
            ret = email.parsingMsg(msg[0][1])
            if ret != {}:
                print('ret :{}'.format(ret))
                doAction(ret)
                
        email.closeFolder(M)
    
    email.logout(M)
    
    print('program done!')

def doAction(msg):
    exchange = msg['exchange']
    coinName = msg['market'][0:3]
    market = msg['market'][3:6]
    action = msg['action']
    
    if(exchange.upper() == 'BITHUMB') :
        if(market.upper() != 'KRW') :
            print('{} has not {} market'.format(exchange,market))
        if(coinName.upper() != 'BTC') :
            print('{} is not support not')
            return
        
        if(action.upper() == 'BUY'):
            buy(coinName)
        elif(action.upper() == 'SELL'):
            sell(coinName)
            
    else :
        print('{} is not support!'.format(exchange))
        return

def buy(coinName):
    #잔고에서 얼마를 가지고 올지 결정한다
    #오더북에서 가장 싼 가격에서 구매를 한다 (미구현)
    #시장가로 오더를 낸다
    fee = bithumb.get_trading_fee()
    balance = bithumb.get_balance('BTC') #balance(보유코인, 사용중코인, 보유원화, 사용중원화)
    marketPrice = bithumb.get_current_price(coinName)
    marketPrice = (int)(marketPrice / 1000)  #BTC의 경우 주문을 1000단위로 넣어야한다. 즉 다른 코인들도 주문 단위가 각각 있을 것이다.
    marketPrice = marketPrice * 1000
    orderCnt = (balance[2] - balance[3]) / marketPrice
    
    feePrice = orderCnt - orderCnt * fee
    print(fee)
    print(feePrice)
    
    print('Buy Order - price : {}\tcnt:{}'.format(marketPrice, orderCnt))
    try:
        desc = bithumb.buy_limit_order(coinName, marketPrice, orderCnt)
        # desc = bithumb.buy_market_order(coinName, orderCnt) #시장가 매수 주문
        
    except Exception as exp:
        print('Error buy order : {}'.format(exp))
    
def sell(coinName):
    #잔고에서 몇개의 코인을 팔지 결정한다
    #오더북에서 가장 비싼 가격에서 판매를 한다(미구현)
    #시장가로 오더를 낸다
    balance = bithumb.get_balance(coinName) #balance(보유코인, 사용중코인, 보유원화, 사용중원화)
    marketPrice = bithumb.get_current_price(coinName)
    marketPrice = (int)(marketPrice / 1000)  #BTC의 경우 주문을 1000단위로 넣어야한다. 즉 다른 코인들도 주문 단위가 각각 있을 것이다.
    marketPrice = marketPrice * 1000
    # orderCnt = keepCnt[coinName] - balance #keepCnt를 구현해야함.. 거래소별 유지해야하는 코인개수
    orderCnt = balance[0] - balance[1]  #코인 전량을 다 팔아버린다.
    
    try:
        desc = bithumb.sell_limit_order(coinName, marketPrice, orderCnt)
        # desc = bithumb.sell_market_order(coinName, orderCnt) 시장가 매도 주문
    except Exception as exp:
        print('Error sell order : {}'.format(exp))
    
if __name__ == '__main__':
    init()
    
    