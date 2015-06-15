import os

import bitcoinrpc

if os.name == 'nt':
    bitcoin_conf = os.path.expanduser("~") + "\\AppData\\Roaming\\Bitcoin\\bitcoin.conf"
else:
    bitcoin_conf = os.path.expanduser("~") + "/.bitcoin/bitcoin.conf"

bitcoind = bitcoinrpc.connect_to_local(filename=bitcoin_conf).proxy