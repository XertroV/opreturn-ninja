op-return-ninja README
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
#prune=1000
disablewallet=1
blocknotify="cd /home/user/prod/opreturn-ninja/ && python -m opreturnninja.on_block --block-hash %s"
```
