from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import BigInteger, DateTime, Float

from crawl import settings

DeclarativeBase = declarative_base()


def db_connect() -> Engine:
    return create_engine(URL(**settings.DATABASE))

def create_items_table(engine: Engine):
    DeclarativeBase.metadata.create_all(engine)

class Items(DeclarativeBase):
    __tablename__ = "prices"
    __table_args__ = { "schema": settings.DATABASE_PG_SCHEMA }

    id = Column("id", BigInteger, primary_key=True)
    object_ref = Column("object_ref", String)
    category = Column("category", String)
    date = Column("date", DateTime)
    flatType = Column("flatType", String)
    floor = Column("floor", String)
    rent = Column("rent", Integer)
    rent_add = Column("rent_add", Integer)
    rent_net = Column("rent_net", Integer)
    rooms = Column("rooms", Float)
    area = Column("area", Integer)
    year_built = Column("year_built", Integer)
    street_number = Column("street_number", String)
    city = Column("city", String)
    zip = Column("zip", String)
    lat = Column("lat", Float)
    lng = Column("lng", Float)
    wkt = Column("wkt", String)
    egid = Column("egid", Integer)

class Addresses(DeclarativeBase):
    __tablename__ = "addresses"
    __table_args__ = { "schema": settings.DATABASE_PG_SCHEMA }

    egid = Column("BDG_EGID", BigInteger, primary_key=True)
    streetname = Column("STN_LABEL", String)
    housenumber = Column("ADR_NUMBER", String)
    zipcode = Column("ZIP_LABEL", String)
    easting = Column("ADR_EASTING", Integer)
    northing = Column("ADR_NORTHING", Integer)
    address_string = Column("ADR_STRING", String)
    geom = Column("_geom", String)
