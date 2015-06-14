import argparse
from io import BytesIO
from binascii import unhexlify, hexlify as _hexlify

import bitcoinrpc

from pycoin.block import Block
from pycoin.tx.TxOut import script_obj_from_script
from pycoin.tx.pay_to.ScriptNulldata import ScriptNulldata

from .models import DBSession, Nulldatas

if __name__ == "__main__":
    def hexlify(raw_bytes):
        if type(raw_bytes) is bytes:
            return _hexlify(raw_bytes).decode()
        return _hexlify(raw_bytes)

    session = DBSession

    parser = argparse.ArgumentParser()
    parser.add_argument('--block-hash', help='Notify of new block hash', type=str, required=True)
    args = parser.parse_args()
    block_hash = args.block_hash

    bitcoind = bitcoinrpc.connect_to_local().proxy
    seralized_block = BytesIO(unhexlify(bitcoind.getblock(args.block_hash, False)))
    block = Block.parse(seralized_block)

    for tx_n, tx in enumerate(block.txs):
        for tx_out_n, tx_out in enumerate(tx.txs_out):
            if tx_out.script[0:1] == b'\x6a':
                script_object = script_obj_from_script(tx_out.script)
                if type(script_object) == ScriptNulldata:
                    session.merge(Nulldatas(in_block_hash=block_hash, txid=hexlify(tx.hash()[::-1]), script=hexlify(tx_out.script), tx_n=tx_n, tx_out_n=tx_out_n))
                    print(script_object, tx.hash())
                    session.commit()
        print(tx)
    session.commit()
