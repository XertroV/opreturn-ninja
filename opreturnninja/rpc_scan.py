import argparse
from io import BytesIO
from binascii import unhexlify, hexlify as _hexlify
from time import sleep

import bitcoinrpc

from sqlalchemy.exc import IntegrityError

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
    parser.add_argument('--block-height', help='Start from this block height', type=int, required=True)
    args = parser.parse_args()
    block_height = args.block_height

    bitcoind = bitcoinrpc.connect_to_local().proxy

    def get_block(block_hash, hex_summary=True):
        return bitcoind.getblock(block_hash, hex_summary)

    def block_as_bytesio(block_hash):
        return BytesIO(unhexlify(get_block(block_hash, False)))

    while True:
        try:
            block_hash = bitcoind.getblockhash(block_height)
            block = Block.parse(block_as_bytesio(block_hash))
            for tx_n, tx in enumerate(block.txs):
                for tx_out_n, tx_out in enumerate(tx.txs_out):
                    if tx_out.script[0:1] == b'\x6a':
                        script_object = script_obj_from_script(tx_out.script)
                        if type(script_object) == ScriptNulldata:
                            session.merge(Nulldatas(in_block_hash=block_hash, txid=hexlify(tx.hash()[::-1]), script=hexlify(tx_out.script), tx_n=tx_n, tx_out_n=tx_out_n))
                            print(script_object, tx.hash(), block_height)
                            session.commit()
            session.commit()

            print('Scanned', block_height)
            block_height += 1
        except KeyboardInterrupt:
            print("Exiting.")
            break
        except IntegrityError as e:
            session.rollback()
            block_height += 1  # probably a duplicate entry
            print(e, 'skipping')
        except Exception as e:
            session.rollback()
            print(e, type(e))
            sleep(1)
