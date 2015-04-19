from collections import defaultdict
import random
import json
from time import time
from datetime import datetime
import socket

from pyramid.view import view_config

from .constants import ELECTRUM_SERVERS, SECONDS_PER_REQUEST

ip_last_request_map = defaultdict(lambda: 0)


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
        while not sent:
            try:
                server = random.choice(list(ELECTRUM_SERVERS.items()))
                s = socket.create_connection(server)
                s.send(json.dumps({"id": "opreturn.ninja-{}".format(time()), "method": "blockchain.transaction.broadcast", "params": [params[0]]}).encode() + b'\n')
                electrum_response = json.loads(s.recv(2048)[:-1].decode())  # the slice is to remove the trailing new line
                electrum_response['id'] = request.json_body['id']
                print(electrum_response, server, time_now)
                return electrum_response
            except ConnectionRefusedError as e:
                print(e, server, time_now)
            except socket.gaierror as e:
                print(e, server, time_now)
            except Exception as e:
                print(e, server, time_now)
                return {'error': str(e)}
    return {
        'result': None,
        'error': 'RPC Request Unknown',
        'id': request.json_body['id'],
    }


@view_config(route_name='index', renderer='templates/index.pt')
def index_view(request):
    return {}