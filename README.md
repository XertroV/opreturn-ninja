opreturn-ninja README
==================

## Requirements

* Python 3 (3.4 assumed)
* Bitcoin Core (for nulldata history)

Running the Web Interface
---------------

```
- cd <directory containing this file>

- $VENV/bin/python setup.py develop

# this step may be required again in the future but for the moment on_block.py isn't
# run with pserve so a db is manually specified in the code.
# - $VENV/bin/initialize_op-return-ninja_db development.ini

- $VENV/bin/pserve development.ini
```


Configuring Bitcoin Core
---------------

opreturn-ninja requires bitcoin core running in the background for the historical API.

#### Sample bitcoin.conf

```
#testnet=1
rpcuser=rpcuser
rpcpassword=g3wlPdnxVvIhUq1F5XdbQroIwIMfpmWPzAUKez0Su01zAIH72NeMQDV5q47Ui4O
server=1
txindex=1
disablewallet=1
blocknotify="cd /home/user/prod/opreturn-ninja/ && python -m opreturnninja.on_block --block-hash %s"
```


## Scanning the blockchain via RPC

```
cd /home/user/prod/opreturn-ninja
python -m opreturnninja.rpc_scan --block-height 1
```

This takes a long while and requires the block to be on the disk.
If you are pruning it must be run as the chain is syncing to ensure you get all the nulldatas.

The script does not terminate and will show `<class 'bitcoinrpc.proxy.JSONRPCException'>` when a block is not available.
It then sleeps 1 second and tries again ad infinitum.