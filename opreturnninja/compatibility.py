import os

from bitcoinrpc.authproxy import AuthServiceProxy

if os.name == 'nt':
    bitcoin_conf = os.path.expanduser("~") + "\\AppData\\Roaming\\Bitcoin\\bitcoin.conf"
else:
    bitcoin_conf = os.path.expanduser("~") + "/.bitcoin/bitcoin.conf"

# bitcoind = bitcoinrpc.connect_to_local(filename=bitcoin_conf).proxy

def gen_bitcoind():
    return AuthServiceProxy("http://%s:%s@127.0.0.1:8332"%('bitcoinrpc','test'))  # this is fing stupid to keep doing, biggest letdown of python-bitcoinrpc, y u no acknowledge how your users want to use the library

bitcoind = gen_bitcoind()
