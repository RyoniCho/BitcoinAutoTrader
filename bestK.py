import pyupbit
import numpy as np


def get_ror(k=0.5):
    df = pyupbit.get_ohlcv("KRW-BTC", count=7)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)
    
    #수익률구하기
    #np.where(조건문,조건이참일때값,조건이거짓일때값)
    #타겟가격보다 고가가 높은상황이라면? 매수가 진행->이때의 수익률은 close때 매도하므로 close/target, 매수가 진행이안된다면 1
    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'],
                         1)
    #누적곱(cumprod). 누적수익률
    ror = df['ror'].cumprod()[-2]
    return ror


def get_bestK():
    maxror=0
    bestK=0
    for k in np.arange(0.1, 1.0, 0.1):
        ror = get_ror(k)
        if ror>maxror:
            maxror=ror
            bestK=k
        print("%.1f %f" % (k, ror))
    result="Best K: {} / ROR: {}".format(bestK,maxror)
    print(result)

    return (bestK,result)


