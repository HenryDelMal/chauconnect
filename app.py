import flask
from flask import request, jsonify
from bitcoin import *
from params import *
from redchaucha import *

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return "Chauconnect API for Casino"

@app.route('/test', methods=['GET'])
def test():
    test_data = {"test1": "hi", "test2": 1312}
    return jsonify(test_data)

@app.route('/new_wallet', methods=['GET'])
def new_wallet():
    privkey = encode_privkey(random_key(), 'wif', magic)
    address = privtoaddr(privkey, magic)
    wallet = {'address': address, 
              'privkey': privkey }
    return jsonify(wallet)

@app.route('/sendtx', methods=['POST'])
def sendtx():
    form = request.form
    return sendTx(form['sender_addr'], form['sender_privkey'], int(form['amount']), form['receptor'], 'casino.cuy.cl')

@app.route('/balance', methods=['GET','POST'])
def balance():
    if request.method == 'POST':
        form = request.form
        data = getbalance(form['addr'])
        info = {'addr': form['addr'], 
                'confirmed': data[0],
                'inputs': data[1],
                'unconfirmed': data[2]}
        return jsonify(info)
    else:
        return 'Only POST >:('

app.run()
