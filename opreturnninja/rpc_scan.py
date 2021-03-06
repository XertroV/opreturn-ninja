import logging
logging.basicConfig(level=logging.INFO)

import argparse
import traceback
import sys
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
from pycoin.tx.script import ScriptError

from .models import DBSession, merge_nulldatas_from_block_obj, have_block, max_block_height, all_block_heights
from .compatibility import gen_bitcoind


def get_block(bitcoind, block_hash, hex_summary=True):
    return bitcoind.getblock(block_hash, hex_summary)


def block_as_bytesio(bitcoind, block_hash):
    return BytesIO(unhexlify(get_block(bitcoind, block_hash, False)))


def block_at_height(block_height):
    _bitcoind = gen_bitcoind(timeout=5)

    while True:
        try:
            block_hash = _bitcoind.getblockhash(block_height)
            block = Block.parse(block_as_bytesio(_bitcoind, block_hash))
            ans = (block, block_hash, block_height)  # order important for merge_nulldatas
            logging.info("Processing results for height %d" % ans[2])
            merge_nulldatas_from_block_obj(*ans, bitcoind=_bitcoind)
            return ans
        except timeout as e:
            logging.warning('%d, Timeout... Creating new bitcoind' % block_height)
        except http.client.CannotSendRequest as e:
            logging.warning("Got CannotSendRequest.")
            traceback.print_tb(e.__traceback__)
        except ScriptError as e:
            logging.error("Script parse error!")
            traceback.print_tb(e.__traceback__)
        except Exception as e:
            logging.warning("%d, %s, %s" % (block_height, e, type(e)))
        finally:
            _bitcoind = gen_bitcoind()
            logging.info("%d; Regen'd bitcoind" % block_height)
            sleep(0.1)


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    session = DBSession

    parser = argparse.ArgumentParser()
    parser.add_argument('--block-height', help='Start from this block height', type=int, required=True)
    parser.add_argument('--n-processes', help='How many processes to use, can be higher than CPU#', type=int, default=1)
    parser.add_argument('--cprofile', help='Use cProfile to monitor performance', action="store_true")
    args = parser.parse_args()
    init_bh = args.block_height
    n_proc = args.n_processes
    logging.info("Got args: %s" % args)

    def main():
        bitcoind = gen_bitcoind(timeout=15)

        try:
            best_block = bitcoind.getbestblockhash()
            force_from = bitcoind.getblock(best_block)['height'] - 144  # force rescan of last day at least
        except Exception as e:
            logging.error("Got exception during startup: %s" % e)
            sys.exit(1)

        # TODO: figure out how to ensure we always have the correct nulldatas available in case of reorg
        logging.info("Top block hash: %s" % best_block)

        start_scan_from = min(force_from, max_block_height(), init_bh)
        logging.info("Scanning from %s" % start_scan_from)

        _ah = all_block_heights()
        logging.info("Reporting %d blocks scanned" % len(_ah))
        existing_heights = set(_ah)

        args = list([i for i in range(start_scan_from + 1, max(430000, force_from + (144 * 365))) if i not in existing_heights])
        logging.info('Have a list of %d args for `block_at_height`' % len(args))
        pool = mp.Pool(n_proc)
        results = pool.imap(block_at_height, args)
        logging.info("Got results object %s" % results)

        for r in results:
            logging.info("Finished processing %s, %s" % (r[1], r[2]))


    if args.cprofile:
        import cProfile
        cProfile.run("main()")
    else:
        main()
