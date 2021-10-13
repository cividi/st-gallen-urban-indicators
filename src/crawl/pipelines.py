from sqlalchemy.orm import sessionmaker

from crawl.models import Items, create_items_table, db_connect


class HomegatePipeline:
    def __init__(self):
        engine = db_connect()
        create_items_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.Session()
        instance = session.query(Items).filter_by(**item).one_or_none()
        if instance:
            return instance
        homegate_item = Items(**item)

        try:
            session.add(homegate_item)
            session.commit()
        except:
            session.rollback()
            return item, False
        finally:
            session.close()
        
        return item