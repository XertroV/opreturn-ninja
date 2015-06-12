from collections import defaultdict
import random
import json
from time import time
from datetime import datetime
import socket

import bitcoinrpc

from pyramid.view import view_config

from .constants import ELECTRUM_SERVERS, SECONDS_PER_REQUEST
from .models import DBSession as session, Nulldatas

ip_last_request_map = defaultdict(lambda: 0)

bitcoind = bitcoinrpc.connect_to_local(filename="C:\\Users\\mkay3730\\AppData\\Roaming\\Bitcoin\\bitcoin.conf").proxy

def rate_limit(f):
    def inner(request, *args, **kwargs):
        global ip_last_request_map
        if time() < ip_last_request_map[request.client_addr] + SECONDS_PER_REQUEST:
            return {'error': 'requested too soon; {} seconds required between calls.'.format(SECONDS_PER_REQUEST)}
        ip_last_request_map[request.client_addr] = time()
        return f(request, *args, **kwargs)
    return inner


@view_config(route_name='api', renderer='json')
@rate_limit
def api_view(request):
    assert hasattr(request, 'json_body')
    assert 'method' in request.json_body and 'params' in request.json_body
    method = request.json_body['method']
    params = request.json_body['params']
    assert type(params) == list
    time_now = datetime.now().isoformat()

    if method == 'sendrawtransaction':
        assert len(params) == 1
        sent = False
        attempts = 0
        while not sent and attempts < 5:
            try:
                server = random.choice(list(ELECTRUM_SERVERS.items()))
                s = socket.create_connection(server)
                s.send(json.dumps({"id": "opreturn.ninja-{}".format(time()), "method": "blockchain.transaction.broadcast", "params": [params[0]]}).encode() + b'\n')
                electrum_response = json.loads(s.recv(2048)[:-1].decode())  # the slice is to remove the trailing new line
                electrum_response['id'] = request.json_body['id']
                print(electrum_response, server, time_now)
                return electrum_response
            except (ConnectionRefusedError, socket.gaierror) as e:
                print(e, server, time_now)
            except Exception as e:
                print(e, server, time_now)
                return {'error': str(e)}
            attempts += 1
    return {
        'result': None,
        'error': 'RPC Request Unknown',
        'id': request.json_body['id'],
    }


@view_config(route_name='api_block', renderer='json')
def api_block_view(request):
    height = int(request.matchdict['height'])
    block_hash = bitcoind.getblockhash(height)
    block_details = bitcoind.getblock(block_hash)
    print(block_hash, block_details)
    nulldatas = session.query(Nulldatas).filter(Nulldatas.in_block_hash == block_hash).all()
    return {
        'height': height,
        'timestamp': block_details['time'],
        'op_returns': [{'txid':n.txid, 'tx_n':n.tx_n, 'tx_out_n':n.tx_out_n, 'script':n.script} for n in nulldatas],
    }


@view_config(route_name='index', renderer='templates/index.pt')
def index_view(request):
    return {}





