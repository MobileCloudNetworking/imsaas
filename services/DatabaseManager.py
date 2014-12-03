import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from util.SysUtil import SysUtil

__author__ = 'mpa'

from util.DatabaseManager import DatabaseManager as ABCDatabaseManager

logger = logging.getLogger("EMMLogger")


class DatabaseManager(ABCDatabaseManager):
    class __DatabaseManager:
        def __init__(self):
            """
            dialect+driver://username:password@host:port/database
            """

            self.conf = SysUtil().get_sys_conf()
            print self.conf.props
            db_username = self.conf.props['db_username']
            db_password = self.conf.props['db_password']
            db_url = self.conf.props['db_url']
            db_name = self.conf.props['db_name']
            self.engine = create_engine('mysql://' + db_username + ':' + db_password + '@' + db_url + '/' + db_name,
                                        echo=True)
            session = sessionmaker(bind=self.engine)
            self.session = session()

        def __str__(self):
            return repr(self) + self.val

        def persist(self, obj):
            self.session.add(obj)
            return obj

        def remove(self, obj):
            self.session.delete(obj)

        def update(self, obj):
            self.session.merge(obj)
            return obj

        def get_all(self, _class):
            return self.session.query(_class).all()

        def get_by_id(self, _class, _id):
            return self.session.query(_class).filter_by(id=_id).one()

        def get_by_name(self, _class, _name):
            return self.session.query(_class).filter_by(name=_name).all()

    instance = None

    def __init__(self):
        if not DatabaseManager.instance:
            DatabaseManager.instance = DatabaseManager.__DatabaseManager()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def persist(self, obj):
        try:
            obj = self.instance.persist(obj)
            self.instance.session.commit()
            logger.debug("Persisted " + str(obj))
        except:
            self.instance.session.rollback()
            raise
        return obj

    def remove(self, obj):
        try:
            obj = self.instance.remove(obj)
            self.instance.session.commit()
        except:
            self.instance.session.rollback()
            raise
        return obj

    def update(self, obj):
        try:
            obj = self.instance.update(obj)
            self.instance.session.commit()
        except:
            self.instance.session.rollback()
            raise
        return obj


    def get_all(self, _class):
        try:
            lst = self.instance.get_all(_class)
            self.instance.session.commit
        except:
            self.instance.session.rollback
            raise
        return lst

    def get_by_id(self, _class, _id):
        try:
            res = self.instance.get_by_id(_class, _id)
            self.instance.session.commit
        except:
            self.instance.session.rollback
            raise
        return res

    def get_by_name(self, _class, _name):
        try:
            res = self.instance.get_by_name(_class, _name)
            self.instance.session.commit
        except:
            self.instance.session.rollback
            raise
        return res