import json

import random

from pyramid.view import view_config

from .constants import ELECTRUM_SERVERS

from bitcoin.rpc import RawProxy, DEFAULT_USER_AGENT

import socket

class RPC(RawProxy):

    def passJson(self, json_to_dump):
        self.__dict__['_RawProxy__conn'].request('POST', self.__dict__['_RawProxy__url'].path, json.dumps(json_to_dump),
                            {'Host': self.__dict__['_RawProxy__url'].hostname,
                             'User-Agent': DEFAULT_USER_AGENT,
                             'Authorization': self.__dict__['_RawProxy__auth_header'],
                             'Content-type': 'application/json'})
        return self._get_response()

    def __getattr__(self, name):
        if name == '__conn':
            return self.__conn
        return RawProxy.__getattr__(self, name)


rpc = RPC()

def setupRpc():
    global rpc
    rpc = RPC()
setupRpc()

@view_config(route_name='api', renderer='json')
def api_view(request):
    global rpc
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
                s = socket.create_connection(random.choice(list(ELECTRUM_SERVERS.items())))
                s.send(b'{"id":"0", "method":"blockchain.transaction.broadcast", "params":["' + params[0].encode() + b'"]}\n')
                r = {'result': s.recv(1024)[:-1].decode(), 'error': None, 'id': request.json_body['id']}  # the slice is to remove the trailing new line
                print(r)
                return r
            except ConnectionRefusedError as e:
                print(e)
            except socket.gaierror as e:
                print(e)
    return {
        'result': None,
        'error': 'RPC Request Unknown',
        'id': request.json_body['id'],
    }



@view_config(route_name='index', renderer='templates/index.pt')
def index_view(request):
    return {}