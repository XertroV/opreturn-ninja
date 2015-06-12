op-return-ninja README
==================



Running the Web Interface
---------------

- cd <directory containing this file>

- $VENV/bin/python setup.py develop

# this step may be required again in the future but for the moment on_block.py isn't
# run with pserve so a db is manually specified in the code.
# - $VENV/bin/initialize_op-return-ninja_db development.ini

- $VENV/bin/pserve development.ini


Configuring Bitcoin Core
---------------

opreturn-ninja requires bitcoin core running in the background for the historical API.

#### Sample bitcoin.conf

```
#testnet=1
rpcuser=rpcuser
rpcpassword=alskdjf98h3fiou4b
server=1
txindex=1
disablewallet=1
blocknotify="cd C:\Users\user\src\opreturn-ninja && python -m opreturnninja.on_block --block-hash %s"
