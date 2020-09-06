from params import COIN, ADDRESS_PREFIX, INSIGHT
from requests import get, post
from bitcoin import *
from binascii import a2b_hex, b2a_hex
import time

def OP_RETURN_payload(string):
    metadata = bytes(string, 'utf-8')
    metadata_len = len(metadata)

    if metadata_len <= 75:
        payload = bytearray((metadata_len,)) + metadata
    elif metadata_len <= 256:
        payload = b"\x4c" + bytearray((metadata_len,)) + metadata
    else:
        payload = b"\x4d" + \
            bytearray((metadata_len % 256,)) + \
            bytearray((int(metadata_len/256),)) + metadata

    return payload

def getbalance(addr):
    unspent = get(INSIGHT + '/api/addr/' + addr + '/utxo').json()

    confirmed = unconfirmed = 0

    inputs = []
    for i in unspent:
        if i['confirmations'] >= 1 and i['amount'] >= 0.001:
            confirmed += i['amount']
            inputs_tx = {
                'output': i['txid'] + ':' + str(i['vout']),
                'value': i['satoshis'],
                'address': i['address']}

            inputs.append(inputs_tx)
        else:
            unconfirmed += i['amount']

    return [confirmed, inputs, unconfirmed]


def sendTx(sender_addr, sender_privkey, amount, receptor, op_return=''):
    addr = sender_addr
    privkey = sender_privkey
    confirmed_balance, inputs, unconfirmed = getbalance(addr)

    if not len(receptor) == 34 and receptor[0] == 'c':
        return "Dirección inválida", 0

    elif amount > confirmed_balance:
        return "Balance insuficiente", 0

    elif amount <= 0:
        return "Monto inválido", 0

    # Transformar valores a Chatoshis
    used_amount = int(amount*COIN)

    # Utilizar solo las unspent que se necesiten
    used_balance = 0
    used_inputs = []

    for i in inputs:
        used_balance += i['value']
        used_inputs.append(i)
        if used_balance > used_amount:
            break

    # Output
    outputs = [{'address': receptor, 'value': used_amount}]

    # OP_RETURN
    if len(op_return) > 0 and len(op_return) <= 255:
        payload = OP_RETURN_payload(op_return)
        script = '6a' + \
            b2a_hex(payload).decode('utf-8', errors='ignore')

        outputs.append({'value': 0, 'script': script})

    # Transacción
    template_tx = mktx(used_inputs, outputs)
    size = len(a2b_hex(template_tx))

    # FEE = 0.01 CHA/kb
    # MAX FEE = 0.1 CHA

    fee = int((size/1024)*0.01*COIN) 
    fee = 1e7 if fee > 1e7 else fee

    print(used_balance)
    print(amount)
    print(fee)

    if used_balance == used_amount:
        outputs[0] = {'address': receptor, 'value': used_amount - fee}
        tx = mktx(used_inputs, outputs)
    else:
        tx = mksend(used_inputs, outputs, addr, fee)

    for i in range(len(used_inputs)):
        tx = sign(tx, i, privkey)
    
    broadcasting = post(INSIGHT + '/api/tx/send', data={'rawtx': tx})

    try:
        msg = INSIGHT + "/tx/%s" % broadcasting.json()['txid']
    except:
        msg = broadcasting.text

    return msg, fee