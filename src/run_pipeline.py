from crawl import settings
from frictionless import Resource
from frictionless.plugins.sql import SqlDialect


db_string = f"{settings.DATABASE['drivername']}://{settings.DATABASE['username']}:{settings.DATABASE['password']}@{settings.DATABASE['host']}:{settings.DATABASE['port']}/{settings.DATABASE['database']}"

res = Resource(
    path=db_string,
    dialect=SqlDialect(
        namespace=settings.DATABASE_PG_SCHEMA,
        table="prices",
        where="wkt is null",
    )
)

print(len(res.read_rows()))
