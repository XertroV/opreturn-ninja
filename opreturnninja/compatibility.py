import os

from bitcoinrpc.authproxy import AuthServiceProxy

from .config import config

def gen_bitcoind(timeout=2):
    return AuthServiceProxy("http://%s:%s@%s:%d"%(config.BITCOIN_RPC_USER, config.BITCOIN_RPC_PASSWORD, config.BITCOIN_RPC_HOST, config.BITCOIN_RPC_PORT), timeout=timeout)

bitcoind = gen_bitcoind()
