import argparse
from io import BytesIO
from binascii import unhexlify

from pycoin.block import Block

from .models import merge_nulldatas_from_block_obj
from .compatibility import bitcoind

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--block-hash', help='Notify of new block hash', type=str, required=True)
    args = parser.parse_args()
    block_hash = args.block_hash

    seralized_block = BytesIO(unhexlify(bitcoind.getblock(args.block_hash, False)))
    json_block = bitcoind.getblock(args.block_hash)
    block = Block.parse(seralized_block)
    merge_nulldatas_from_block_obj(block, block_hash, json_block['height'], verbose=True)
