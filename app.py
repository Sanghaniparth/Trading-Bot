from flask import *
import config
from binance.client import Client
from binance.enums import *
from pymongo import MongoClient 
import ast
import requests
import json

app = Flask(__name__)
# app.secret_key = b'somelongrandomstring'
clt = MongoClient('mongodb://localhost:27017/tradingbot')
db = clt.tradingbot
col = db.ORDER
col1 = db.BALANCE
client = Client(config.API_KEY, config.SECRET_KEY, tld='com')

d = {}
d1 = {}
API_KEY = 'KBiHlUVMFS82rCeNvXexfiH4SxaOAHljhMbe0na8IH4fMZgLq4MMSc7zIGaypkBt'
SECRET_KEY = 'siZWVbcFn1XNXqFGWfh1HWAgAOwKEb737ZVPBnbRdpznd7PxYjS6tn4gs5KF7sPm'
client = Client(API_KEY,SECRET_KEY,tld='com')

@app.route('/')
def login():
    title = 'Login'
    return render_template('login.html', title=title)

@app.route('/register')
def register():
    title = 'Register'
    return render_template('register.html', title=title)

@app.route('/binance_config')
def binance_config():
    title = 'Configration'
    return render_template('binance_config.html',title=title)

@app.route('/acc_balance/<my_balances>')
def acc_balance(my_balances):
    title = 'Blanace'
    balance = ast.literal_eval(my_balances)
    return render_template('acc_balance.html',title=title,my_balances=balance)

@app.route('/index')
def index():
    title = 'Trading Bot'
    url = "https://api.binance.com/api/v3/ticker/price"
    price = requests.get(url).json()
    return render_template('index.html', title=title,price=price)

@app.route('/login_validation', methods = ['POST'])
def login_validation():
    email = request.form['Email']
    password = request.form['Password']
    d1['Email'] = email
    d1['password'] = password
    data = col.find({},{"_id": False})
    for i in data:
        if d1 == i:
            return redirect('/binance_config')
    else:
        return redirect('/register')

@app.route('/add_user',methods = ['POST'])
def add_user():
    uemail = request.form['Email']
    upassword = request.form['Password']
    d['Email'] = uemail
    d['password'] = upassword
    col.insert_one(d)
    return redirect('/')

@app.route('/configration', methods = ['POST'])
def configration():
    API_KEY = request.form['API_KEY']
    SECRET_KEY = request.form['SECRET_KEY']
    client = Client(API_KEY,SECRET_KEY,tld='com')
    balance = client.get_account()
    balances = balance['balances']
    print(type(balances))
    return redirect(url_for('acc_balance', my_balances = balances))

@app.route('/trade')
def trade():
    title = 'Trade History'
    orders = client.get_all_orders (symbol='BNBBTC', limit=10)
    return render_template('trade.html', title = title, order = orders)

@app.route('/tradestart', methods = ['POST'])
def tradestart():
    #conditon
    symbol = request.form['symbol']
    quantity = request.form['quantity']
    rsi_period = request.form['rsi_period']
    overbought = request.form['overbought']
    oversell = request.form['oversell']
    return redirect('trade')

@app.route('/history')
def history():
    candlesticks = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_15MINUTE, "1 Oct, 2022")

    processed_candlesticks = []

    for data in candlesticks:
        candlestick = { 
            "time": data[0] / 1000, 
            "open": data[1],
            "high": data[2], 
            "low": data[3], 
            "close": data[4]
        }

        processed_candlesticks.append(candlestick)

    return jsonify(processed_candlesticks)


