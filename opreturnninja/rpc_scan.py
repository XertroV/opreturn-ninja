import argparse
from io import BytesIO
from binascii import unhexlify
from time import sleep

from sqlalchemy.exc import IntegrityError

from pycoin.block import Block

from .models import DBSession, merge_nulldatas_from_block_obj
from .compatibility import bitcoind

if __name__ == "__main__":
    session = DBSession

    parser = argparse.ArgumentParser()
    parser.add_argument('--block-height', help='Start from this block height', type=int, required=True)
    args = parser.parse_args()
    block_height = args.block_height

    def get_block(block_hash, hex_summary=True):
        return bitcoind.getblock(block_hash, hex_summary)

    def block_as_bytesio(block_hash):
        return BytesIO(unhexlify(get_block(block_hash, False)))

    while True:
        try:
            block_hash = bitcoind.getblockhash(block_height)
            block = Block.parse(block_as_bytesio(block_hash))
            merge_nulldatas_from_block_obj(block, block_hash, block_height, verbose=True)
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
