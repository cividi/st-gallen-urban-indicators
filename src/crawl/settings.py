import os

BOT_NAME = "rentalmarket_crawl"
SPIDER_MODULES = ["crawl.spiders"]
NEWSPIDER_MODULE = "crawl.spiders"
ROBOTSTXT_OBEY = True
ITEM_PIPELINES = {
    "crawl.pipelines.HomegatePipeline": 300
}
DATABASE = {
    "drivername": "postgresql",
    "host": os.environ["POSTGRES_HOST"],
    "port": os.environ["POSTGRES_PORT"],
    "username": os.environ["POSTGRES_USER"],
    "password": os.environ["POSTGRES_PASS"],
    "database": os.environ["POSTGRES_DB"],
}
DATABASE_PG_SCHEMA = os.environ["POSTGRES_SCHEMA"]
LOG_LEVEL = "INFO"
DOWNLOAD_DELAY = 1
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15"