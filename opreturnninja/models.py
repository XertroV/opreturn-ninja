from sqlalchemy import Column, Index, Integer, Text,  String, Boolean, create_engine, Index

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

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

Index('index_nulldatas', Nulldatas.in_block_hash, Nulldatas.txid, Nulldatas.tx_n, Nulldatas.tx_out_n, unique=True)

Base.metadata.create_all(engine)