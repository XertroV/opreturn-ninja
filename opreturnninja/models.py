from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    String,
    Boolean,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Nulldatas(Base):
    __tablename__ = 'nulldatas'
    id = Column(Integer, primary_key=True)
    in_block_hash = Column(String)
    txid = Column(String)
    script = Column(String)
    txn = Column(Integer)