from binascii import hexlify as _hexlify
import logging

from pycoin.tx.pay_to import script_obj_from_script, ScriptNulldata
from pycoin.tx.script import ScriptError

from sqlalchemy import Column, Integer,  String, create_engine, Index, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from .compatibility import bitcoind
from .config import config
from .pid_guard import add_engine_pidguard


def hexlify(raw_bytes):
    if type(raw_bytes) is bytes:
        return _hexlify(raw_bytes).decode()
    return _hexlify(raw_bytes)


engine = create_engine(config.DATABASE_URL)#, echo=True)
add_engine_pidguard(engine)
DBSession = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()


def provide_session(f):
    def inner(*args, **kwargs):
        session = scoped_session(sessionmaker(bind=create_engine(config.DATABASE_URL)))
        f(*args, **kwargs, session=session)
    return inner


class Blocks(Base):
    __tablename__ = 'blocks'
    id = Column(Integer, primary_key=True)
    block_hash = Column(String, unique=True, index=True)
    height = Column(Integer, index=True)
    prev_block_hash = Column(String)


# class Heights(Base):
#     __tablename__ = 'heights'
#     height = Column(Integer, primary_key=True)
#     hash = Column(String(64), unique=True, index=True)


def have_block(block_height, session=DBSession):
    if len(session.query(Blocks).filter(Blocks.height == block_height).all()) == 0:
        return False
    return True


def get_block_by_hash(block_hash, session=DBSession):
    return session.query(Blocks).filter(Blocks.block_hash == block_hash).first()


def max_block_height(session=DBSession):
    _height = session.query(func.max(Blocks.height)).one()[0]
    return _height

def all_block_heights(session=DBSession):
    _heights = list(map(lambda e: e[0], session.query(Blocks.height).all()))
    return _heights


class Nulldatas(Base):
    __tablename__ = 'nulldatas'
    id = Column(Integer, primary_key=True)
    in_block_hash = Column(String)
    txid = Column(String)
    script = Column(String)
    tx_n = Column(Integer)
    tx_out_n = Column(Integer)
    timestamp = Column(Integer)
    sender = Column(String)


def n_nulldatas():
    return DBSession.query(func.count(Nulldatas.id)).scalar()


def merge_nulldatas_from_block_obj(block, block_hash, block_height, verbose=True, session=DBSession, bitcoind=bitcoind):
    try:
        if get_block_by_hash(block_hash) is not None:
            logging.info("already merged block %d, %s" % (block_height, block_hash))
            return  # we have this block already
        for tx_n, tx in enumerate(block.txs):
            for tx_out_n, tx_out in enumerate(tx.txs_out):
                if tx_out.script[0:1] == b'\x6a':
                    try:
                        script_object = script_obj_from_script(tx_out.script)
                    except ScriptError as e:
                        logging.warning("Found OP_RETURN tx with bad nulldata: %s, %d" % (tx.hash()[::-1], tx_out_n))
                        continue
                    if type(script_object) == ScriptNulldata:
                        id_tx_reference = tx.txs_in[0]  # tx containing the identity
                        if id_tx_reference.is_coinbase():
                            sender_address = 'COINBASE'
                        else:
                            id_tx_json = bitcoind.getrawtransaction(hexlify(id_tx_reference.previous_hash[::-1]), 1)
                            sender_address = id_tx_json['vout'][id_tx_reference.previous_index]['scriptPubKey']['addresses'][0]
                        session.merge(Nulldatas(in_block_hash=block_hash, txid=hexlify(tx.hash()[::-1]), script=hexlify(tx_out.script), tx_n=tx_n, tx_out_n=tx_out_n, timestamp=block.timestamp, sender=sender_address))
                        if verbose:
                            logging.info("%s, %s, %s" % (script_object, tx.hash(), block_height))
        session.merge(Blocks(block_hash=block_hash, height=block_height, prev_block_hash=block.previous_block_id()))
    except Exception as e:
        session.rollback()
        raise e
    else:
        session.commit()
    if verbose:
        logging.info('Scanned %s' % block_height)

Index('index_nulldatas', Nulldatas.in_block_hash, Nulldatas.txid, Nulldatas.tx_n, Nulldatas.tx_out_n, unique=True)

Base.metadata.create_all(engine)
logging.info('created tables')
