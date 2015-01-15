import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import scoped_session
from emm_exceptions.NotFoundException import NotFoundException

from interfaces.DatabaseManager import DatabaseManager as ABCDatabaseManager
from model import Entities
from util.SysUtil import SysUtil


__author__ = 'mpa'

logger = logging.getLogger("IMSSO")

import threading

Base = declarative_base()

def synchronized(method):
    """ Work with instance method only !!! """
    def new_method(self, *arg, **kws):
        with self.lock:
            return method(self, *arg, **kws)
    return new_method


class DatabaseManager(ABCDatabaseManager):
    class __DatabaseManager:
        lock = threading.RLock()

        def create_session(self):
            self.session = self._scoped_session()

        def __init__(self):
            """
            dialect+driver://username:password@host:port/database
            """

            self.conf = SysUtil().get_sys_conf()
            db_username = self.conf['db_username']
            db_password = self.conf['db_password']
            db_url = self.conf['db_url']
            db_name = self.conf['db_name']
            self.info = 'mysql://' + db_username + ':' + db_password + '@' + db_url + '/' + db_name
            #self.engine = create_engine(self.info, echo=False)
            self.engine = create_engine('sqlite://')
            self._scoped_session = scoped_session(sessionmaker(bind=self.engine, expire_on_commit=False))
            self.session = None
            # self.create_session()

        def __str__(self):
            return repr(self)

        def persist(self, obj):
            self.create_session()
            self.session.add(obj)
            return obj

        def remove(self, obj):
            self.create_session()
            self.session.delete(obj)

        def update(self, obj):
            self.create_session()
            obj = self.session.merge(obj)
            return obj

        def get_all(self, _class):
            self.create_session()
            res = self.session.query(_class).all()
            return res

        def get_by_id(self, _class, _id):
            self.create_session()
            try:
                res = self.session.query(_class).filter_by(id=_id).one()
            except Exception as e:
                raise NotFoundException('No object was found in table ' + _class.__name__ + " with id " + str(_id))
            return res

        def get_by_name(self, _class, _name):
            self.create_session()
            res = self.session.query(_class).filter_by(name=_name).all()
            return res

        def get_by_service_type(self, _class, _type):
            self.create_session()
            res = self.session.query(_class).filter_by(service_type=_type).all()
            return res

    instance = None

    def __init__(self):
        if not DatabaseManager.instance:
            DatabaseManager.instance = DatabaseManager.__DatabaseManager()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    @synchronized
    def persist(self, obj):
        try:
            obj = self.instance.persist(obj)
            self.instance.session.commit()
            logger.info("Persisted " + str(obj))
            self.instance.session.expunge_all()
            self.instance.session.close()
        except:
            self.instance.session.rollback()
            raise
        return obj

    @synchronized
    def remove(self, obj):
        try:
            logger.info("Removing Object " + str(obj))
            obj = self.instance.remove(obj)
            self.instance.session.commit()
            logger.debug('Removed Obj')
            self.instance.session.expunge_all()
            self.instance.session.close()
        except:
            self.instance.session.rollback()
            raise
        return obj

    @synchronized
    def update(self, obj):
        try:
            obj = self.instance.update(obj)
            self.instance.session.commit()
            logger.info("Updated " + str(obj))
            self.instance.session.expunge_all()
            self.instance.session.close()
        except:
            self.instance.session.rollback()
            raise
        return obj

    @synchronized
    def get_all(self, _class):
        try:
            lst = self.instance.get_all(_class)
            self.instance.session.commit
            logger.info('Get all of ' + _class.__name__)
            self.instance.session.expunge_all()
            self.instance.session.close()
        except:
            self.instance.session.rollback
            raise
        return lst

    @synchronized
    def get_by_id(self, _class, _id):
        try:
            res = self.instance.get_by_id(_class, _id)
            self.instance.session.commit
            logger.debug('Get by id ' + repr(_id) + ' of class ' + _class.__name__)
            self.instance.session.expunge_all()
            self.instance.session.close()
        except:
            self.instance.session.rollback
            raise
        return res

    @synchronized
    def get_by_name(self, _class, _name):
        try:
            res = self.instance.get_by_name(_class, _name)
            self.instance.session.commit
            logger.info('Get all of ' + _class.__name__ + ' with name ' + _name)
            self.instance.session.expunge_all()
            self.instance.session.close()
        except:
            self.instance.session.rollback
            raise
        return res

    @synchronized
    def get_by_service_type(self, _class, _type):
        try:
            res = self.instance.get_by_service_type(_class, _type)
            self.instance.session.commit
            logger.debug('Get all of service_type ' + _type)
            self.instance.session.expunge_all()
            self.instance.session.close()
        except:
            self.instance.session.rollback
            raise
        return res

    def create_tables(self):
        print "db_password is %s" %self.info
        Entities.create_tables(self.instance.engine)