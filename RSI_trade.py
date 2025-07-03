import websocket
import json
import pprint
import numpy as np
import talib
from binance.client import Client
from binance.enums import *
from pymongo import MongoClient
from app import *

clt = MongoClient('mongodb://localhost:27017/RSI_TRADE')
db = clt.RSI_TRADE
col = db.ORDER
col1 = db.BALANCE

# API_KEY = ''
# API_SECRET = ''

oversell = oversell
rsi_period = rsi_period
overbought = overbought
trade_symbol = trade_symbol
quantity = quantity      #should be of minimum 10$


SOCKET = "wss://stream.binance.com:9443/ws/{}@kline_1m".format(trade_symbol.lower())
closes = []
position = False
# client = Client(API_KEY,API_SECRET,tld='com')
client = client

def order(side, quantity, symbol, closes, order_type=ORDER_TYPE_MARKET):

    #store  balance
    print("Balances.....")
    balance = client.get_account()
    balances = balance['balances']
    # col1.insert_one(balances)
    # print(balances)
    last_close =  closes[-1]
    print("order start/close at :",last_close)
    try:
        #store order
        order = client.create_order(symbol=symbol, side=side, quantity=quantity, type=order_type)
        print(order)
        for i in order:
            col.insert_one(i)
    except Exception as e:
        print("Error {}".format(e))
        return False

    return True

def on_open(ws):
    print("open")

def on_close(ws):
    print("close")

def on_message(ws, message):
    j_msg = json.loads(message)
    # pprint.pprint(j_msg)
    candle = j_msg['k']
    is_candle_close = candle['x']
    close = candle['c']
    sell = 0

    if is_candle_close:
        closes.append(float(close))
        print("closes:",closes)

        if len(closes) > rsi_period:
            np_closes = np.array(closes)
            rsi = talib.RSI(np_closes,rsi_period)
            print("calulated rsi = ")
            print(rsi)
            last_rsi = rsi[-1]
            print("Last rsi = ",last_rsi)

            global position
            if last_rsi > overbought:
                if position:
                    print("Sell!!")
                    sell = sell + 1
                    order_succeessed = order(SIDE_SELL, quantity,trade_symbol,closes)
                    if sell == 5:
                        on_close(ws)
                    if order_succeessed:
                        position = False
                else:
                    print("You don't have it!")

            if last_rsi < oversell:
                if position:
                    print("You have it!")
                else:
                    print("Buy!!")
                    order_succeessed = order(SIDE_BUY, quantity,trade_symbol,closes)
                    if order_succeessed:
                        position = True


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()

