import argparse
from io import StringIO
from binascii import unhexlify

from bitcoinrpc.authproxy import AuthServiceProxy
from pycoin.block import Block
from pycoin.tx.TxOut import script_obj_from_script
from pycoin.tx.pay_to.ScriptNulldata import ScriptNulldata

from .models import DBSession, Nulldatas

session = DBSession

parser = argparse.ArgumentParser()
parser.add_argument('--block-hash', help='Notify of new block hash', type=str, required=True)
args = parser.parse_args()

bitcoind = AuthServiceProxy("http://foo:bar@127.0.0.1:8332")
seralized_block = StringIO(unhexlify(bitcoind.getblock(args.block_hash, False)['result']))
block = Block.parse(seralized_block)

tx_count = 0
for tx in block.txs:
    for tx_out in tx.txs_out:
        script_object = script_obj_from_script(tx_out.script)
        if type(script_object) == ScriptNulldata:
            session.merge(Nulldatas(in_block_hash=block.hash(), txid=tx.hash(), script=tx_out.script, txn=tx_count))
    tx_count += 1
