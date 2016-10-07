import argparse
from io import BytesIO
from binascii import unhexlify
from time import sleep
import logging
from socket import timeout
import http.client
import multiprocessing as mp
import functools

from sqlalchemy.exc import IntegrityError

from pycoin.block import Block

from .models import DBSession, merge_nulldatas_from_block_obj, have_block, max_block_height, all_block_heights
from .compatibility import gen_bitcoind


def f(func, args):
    return func(*args)

def fstar(args):
    return f(*args)


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    session = DBSession

    parser = argparse.ArgumentParser()
    parser.add_argument('--block-height', help='Start from this block height', type=int, required=True)
    parser.add_argument('--n-processes', help='How many processes to use, can be higher than CPU#', type=int, default=1)
    args = parser.parse_args()
    init_bh = args.block_height
    n_proc = args.n_processes
    print("Got args: %s" % args)

    pace_q_size = n_proc
    pace_q = mp.Queue(pace_q_size)
    for i in range(pace_q_size - 2):
        pace_q.put(True)

    def get_block(bitcoind, block_hash, hex_summary=True):
        return bitcoind.getblock(block_hash, hex_summary)

    def block_as_bytesio(bitcoind, block_hash):
        return BytesIO(unhexlify(get_block(bitcoind, block_hash, False)))

    def block_at_height(block_height):
        _bitcoind = gen_bitcoind()
        pace_q.get()

        while True:
            try:
                block_hash = _bitcoind.getblockhash(block_height)
                block = Block.parse(block_as_bytesio(_bitcoind, block_hash))
                print("Got block: %s" % block)
                ans = (block, block_hash, block_height)
                print("Processing results for height %d" % ans[2])
                merge_nulldatas_from_block_obj(*ans)
                return ans
            except timeout as e:
                logging.warning('Timeout... Creating new bitcoind')
            except Exception as e:
                logging.warning("%d, %s, %s" % (block_height, e, type(e)))
                sleep(5)
            finally:
                _bitcoind = gen_bitcoind()

    bitcoind = gen_bitcoind()
    best_block = bitcoind.getbestblockhash()
    force_from = bitcoind.getblock(best_block)['height'] - 144  # force rescan of last day at least
    # TODO: figure out how to ensure we always have the correct nulldatas available in case of reorg
    print("Top block hash: %s" % best_block)

    start_scan_from = min(force_from, max_block_height(), init_bh)
    print("Scanning from %s" % start_scan_from)

    _ah = all_block_heights()
    existing_heights = set(_ah)

    args = [i for i in range(start_scan_from + 1, force_from + (144 * 365)) if i not in existing_heights]
    pool = mp.Pool(n_proc)
    results = pool.imap(block_at_height, args)
    print("Got results object %s" % results)

    for r in results:
        print("Got results %s" % r)
        pace_q.put(True)
