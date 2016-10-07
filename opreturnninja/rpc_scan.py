import argparse
from io import BytesIO
from binascii import unhexlify
from time import sleep
import logging
from socket import timeout
import http.client
import multiprocessing
import functools

from sqlalchemy.exc import IntegrityError

from pycoin.block import Block

from .models import DBSession, merge_nulldatas_from_block_obj, have_block
from .compatibility import gen_bitcoind

if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    session = DBSession

    parser = argparse.ArgumentParser()
    parser.add_argument('--block-height', help='Start from this block height', type=int, required=True)
    args = parser.parse_args()
    init_bh = args.block_height

    def get_block(bitcoind, block_hash, hex_summary=True):
        return bitcoind.getblock(block_hash, hex_summary)

    def block_as_bytesio(bitcoind, block_hash):
        return BytesIO(unhexlify(get_block(bitcoind, block_hash, False)))

    def block_at_height(block_height, force=False):
        if not force and have_block(block_height):
            logging.warning("Already have block at height %d" % block_height)
            return

        _bitcoind = gen_bitcoind()

        while True:
            try:
                block_hash = _bitcoind.getblockhash(block_height)
                block = Block.parse(block_as_bytesio(_bitcoind, block_hash))
                merge_nulldatas_from_block_obj(block, block_hash, block_height, verbose=True)
                break
            except timeout as e:
                logging.warning('Timeout... Creating new bitcoind')
            except http.client.CannotSendRequest as e:
                logging.warning("%d, %s, %s" % (block_height, e, type(e)))
                sleep(60)
            except Exception as e:
                logging.warning("%d, %s, %s" % (block_height, e, type(e)))
                sleep(5)

    bitcoind = gen_bitcoind()
    best_block = bitcoind.getbestblockhash()
    force_from = bitcoind.getblock(best_block)['height'] - 144  # force rescan of last day at least
    # TODO: figure out how to ensure we always have the correct nulldatas available in case of reorg
    print("Top block hash: %s" % best_block)

    args = [(i, (i >= force_from)) for i in range(init_bh, 10**7)]
    pool = multiprocessing.Pool(10)
    pool.starmap(block_at_height, args, chunksize=1)

