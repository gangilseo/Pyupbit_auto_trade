import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm, tqdm_notebook
import os
import pyupbit

from matplotlib import rcParams

import datetime
import time

import warnings
warnings.filterwarnings("ignore")

__author__ = "Gangil Seo"

#%%

tickers = pyupbit.get_tickers(fiat = "KRW")

price = pyupbit.get_current_price(tickers)

access_key = "geUCOAKYqSZKKtyif8uO24aHcBOx1zBBmyUc3MyS"
secret_key = "FnfkkcRJjDQLZljVveVnturBhTFSsojumqJxHxnI"

upbit = pyupbit.Upbit(access = access_key, secret = secret_key)

# KRW-XRP 매수 주문 >> 1305원 / 5개
# upbit.buy_limit_order("KRW-XRP", 1305, 5)

# KRW-XRP 매도 주문 >> 1315원 / 5개
# upbit.sell_limit_order("KRW-XRP", 1315, 5)

# 대산 300,000 / 나 109,417

#%%
def get_target_price(ticker, k):
    df = pyupbit.get_ohlcv(ticker)
    yesterday = df.iloc[-2]

    today_open = yesterday['close']
    yesterday_high = yesterday['high']
    yesterday_low = yesterday['low']
    target = today_open + (yesterday_high - yesterday_low) * k

    return float(target)

def buy_crypto_currency(ticker):
    krw = upbit.get_balance() * 0.999
    orderbook = pyupbit.get_orderbook(ticker)
    sell_price = orderbook[0]["orderbook_units"][0]["ask_price"]
    unit = krw/float(sell_price)
    upbit.buy_limit_order(ticker, sell_price, unit)

def sell_crypto_currency(ticker):
    orderbook = pyupbit.get_orderbook(ticker)
    bid_price = orderbook[0]["orderbook_units"][0]["bid_price"]
    unit = upbit.get_balances()[-1]["balance"]

    upbit.sell_limit_order(ticker, bid_price, unit)

def get_yesterday_ma(ticker, days, interval = "day"):
    df = pyupbit.get_ohlcv(ticker, interval = interval)
    close = df['close']
    ma = close.rolling(days).mean()

    return float(ma[-2])

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

#%%
# ticker = "KRW-DOGE"
# k = 0.525

# ticker = "KRW-XRP"
# k = 0.225

# ticker = "KRW-MBL"
# k = 0.125

ticker = "KRW-MVL"
k = 0.15


target_price = get_target_price(ticker = ticker, k = k)

time_now = datetime.datetime.now()
time_midnight = datetime.datetime(time_now.year, time_now.month, time_now.day) + datetime.timedelta(1)

while True:
    try:
        time_now = datetime.datetime.now()
        start_tim = get_start_time(ticker)
        end_time = start_time + datetime.timedelta(days = 1)

        if start_time < time_now < end_time - datetime.timedelta(seconds = 10):
            target_price = get_target_price(ticker, k = k)
            print(f"TARGET PRICE: {target_price}")

            sell_crypto_currency(ticker)

        current_price = pyupbit.get_current_price(ticker)
        if (current_price >= target_price) & (current_price >= get_yesterday_ma(ticker, 5)):
            krw = get_balance("KRW")
            if krw > 5000:
                buy_crypto_currency(ticker)

        avg_price = float(upbit.get_balances()[-1]["avg_buy_price"])
        if (current_price < avg_price * 0.98):
            sell_crypto_currency(ticker)
        time.sleep(1)


    except Exception as e:
        print(e)

        time.sleep(1)

