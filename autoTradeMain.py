

import pyupbit
import time
import datetime
import requests
import telegramMessage
import bestK
import sys

accessKey='==Upbit Access KEY=='
secretKey='==Upbit Secret KEY=='


def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_balance(upbit,coin):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == coin:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

def StartAutoTrade(coin):
    
    targetK=0.5
    message=telegramMessage.message()

    # 로그인
    try:
        with open("./upbitKey.txt") as f:
            lines = f.readlines()
            accessKey = lines[0].strip()
            secretKey = lines[1].strip()
        
        upbit = pyupbit.Upbit(accessKey, secretKey)
        print("autotrader start")

        # 시작시 텔레그램에 시작메세지 전송
        message.send_message("비트코인 자동매매 시작합니다.")

        minimumTradePrice=GetMinimumPrice(upbit,coin)
        print(minimumTradePrice)
    except Exception as e:
        print(e)
       
        message.send_message("Exception:: {}".format(e))
        


    while True:
        try:
            now = datetime.datetime.now()
            start_time = get_start_time(coin)
            end_time = start_time + datetime.timedelta(days=1)

            if start_time < now < end_time - datetime.timedelta(seconds=10):
                target_price = get_target_price(coin, targetK)
                ma15 = get_ma15(coin)
                current_price = get_current_price(coin)
                if target_price < current_price and ma15 < current_price:
                    krw = float(upbit.get_balance('KRW'))
                    if krw > minimumTradePrice:
                        buy_result = upbit.buy_market_order(coin, krw*0.9995)
                        message.send_message("{} 매수 : {}".format(coin,str(buy_result)))
            else:
                btc = float(upbit.get_balance(coin))
                if btc > 0:
                    #전부매도
                    sell_result = upbit.sell_market_order(coin, btc) 
                    message.send_message("{} 매도 : {}".format(coin,str(sell_result)))
                targetK,kResult= bestK.get_bestK()
                message.send_message("<<Best K Result>> :: \n{}".format(kResult))

            #Telegram Bot(Response Message)
            messageId=message.CheckMessageInLoop()

            if messageId==message.currentState:
                CheckCurrentCondition(coin,message)
            elif messageId==message.bestKUpdate:
                targetK,kResult= bestK.get_bestK()
                message.send_message("<<Best K Update>> :: \n{}".format(kResult))
            elif messageId==message.exit:
                message.send_message("자동매매봇을 종료하시겠습니까?(네/아니오)")
            elif messageId==message.exitYes:
                message.send_message("자동매매봇이 종료되었습니다")
                sys.exit()


            time.sleep(1)
        except Exception as e:
            print(e)
            message.send_message("Exception:: {}".format(e))
            time.sleep(1)




def GetMinimumPrice(upbit,coin):
    result=upbit.get_chance(coin,True)
    return float(result[0]['market']['bid']['min_total'])
   

def CheckCurrentCondition(coin,message):
   
    target_price = get_target_price(coin, 0.5)
    ma15 = get_ma15(coin)
    current_price = get_current_price(coin)

    print("Target Price: {}".format(target_price))
    print("Current Price: {}".format(current_price))
    print("MA15 Price: {}".format(ma15))

    text="[타겟가격]: {}\n[현재가격]: {}\n[15일 이동평균선가격]\n{}\n".format(target_price,current_price,ma15)
    
    if target_price < current_price:
        text+='현재가격이 타겟가격보다 높습니다.\n'
        print('targetPrice<currentPrice')
       
    if ma15 < current_price:
        text+='현재가격이 15일 이동평균선보다 높습니다.\n'
        print("ma15 < current_price")    
    message.send_message(text)

StartAutoTrade("KRW-ETH")
