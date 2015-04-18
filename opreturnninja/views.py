from collections import defaultdict

import random

from time import time

from pyramid.view import view_config

from .constants import ELECTRUM_SERVERS

from bitcoin.rpc import RawProxy, DEFAULT_USER_AGENT

import socket

ip_last_request_map = defaultdict(lambda: 0)

def rate_limit(f):
    def inner(request, *args, **kwargs):
        global ip_last_request_map
        if time() < ip_last_request_map[request.client_addr] + 2:
            return {'error': 'requested too soon; 2 seconds required between calls.'}
        ip_last_request_map[request.client_addr] =  time()
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
    if method == 'sendrawtransaction':
        assert len(params) == 1
        sent = False
        while not sent:
            try:
                server = random.choice(list(ELECTRUM_SERVERS.items()))
                s = socket.create_connection(server)
                s.send(b'{"id":"0", "method":"blockchain.transaction.broadcast", "params":["' + params[0].encode() + b'"]}\n')
                r = {'result': s.recv(1024)[:-1].decode(), 'error': None, 'id': request.json_body['id']}  # the slice is to remove the trailing new line
                print(r, server)
                return r
            except ConnectionRefusedError as e:
                print(e, server)
            except socket.gaierror as e:
                print(e, server)
            except Exception as e:
                print(e, server)
    return {
        'result': None,
        'error': 'RPC Request Unknown',
        'id': request.json_body['id'],
    }



@view_config(route_name='index', renderer='templates/index.pt')
def index_view(request):
    return {}