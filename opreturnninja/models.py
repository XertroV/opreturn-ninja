from binascii import hexlify as _hexlify

from pycoin.tx.pay_to import script_obj_from_script, ScriptNulldata

from sqlalchemy import Column, Index, Integer, Text,  String, Boolean, create_engine, Index

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension


def hexlify(raw_bytes):
    if type(raw_bytes) is bytes:
        return _hexlify(raw_bytes).decode()
    return _hexlify(raw_bytes)


engine = create_engine('sqlite:///opreturn.sqlite', connect_args={'timeout': 15})#, echo=True)
DBSession = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()


class Nulldatas(Base):
    __tablename__ = 'nulldatas'
    id = Column(Integer, primary_key=True)
    in_block_hash = Column(String)
    txid = Column(String)
    script = Column(String)
    tx_n = Column(Integer)
    tx_out_n = Column(Integer)


def merge_nulldatas_from_block_obj(block, block_hash=None, block_height=None, verbose=False):
    session = DBSession
    if block_hash is None:
        block_hash = hexlify(block.hash()[::-1])
    if block_height is None:
        block_height = block_hash
    for tx_n, tx in enumerate(block.txs):
        for tx_out_n, tx_out in enumerate(tx.txs_out):
            if tx_out.script[0:1] == b'\x6a':
                script_object = script_obj_from_script(tx_out.script)
                if type(script_object) == ScriptNulldata:
                    session.merge(Nulldatas(in_block_hash=block_hash, txid=hexlify(tx.hash()[::-1]), script=hexlify(tx_out.script), tx_n=tx_n, tx_out_n=tx_out_n))
                    if verbose:
                        print(script_object, tx.hash(), block_height)
    session.commit()
    if verbose:
        print('Scanned', block_height)

Index('index_nulldatas', Nulldatas.in_block_hash, Nulldatas.txid, Nulldatas.tx_n, Nulldatas.tx_out_n, unique=True)

Base.metadata.create_all(engine)