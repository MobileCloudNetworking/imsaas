# Copyright 2014 Technische Universitaet Berlin
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import ScopedSession as scoped_session
from sqlalchemy.pool import StaticPool

from emm_exceptions.NotFoundException import NotFoundException

from interfaces.DatabaseManager import DatabaseManager as ABCDatabaseManager
from model import Entities
from util.SysUtil import SysUtil


__author__ = 'mpa'

logger = logging.getLogger(__name__)

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

            self.engine = create_engine('sqlite://', connect_args={'check_same_thread':False},
                    poolclass=StaticPool)
            self._scoped_session = scoped_session(sessionmaker(bind=self.engine, expire_on_commit=True))
            self.session = None
            # self.create_session()

        def __str__(self):
            return repr(self)

        def persist(self, obj):
            self.create_session()
            self.session.add(obj)
            obj = self.session.merge(obj)
            return obj

        def remove(self, obj):
            self.create_session()
            obj = self.session.merge(obj)
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
            logger.info('Persisting Object: %s' % id(obj))
            obj = self.instance.persist(obj)
            self.instance.session.commit()
            logger.debug('Persisted Object: %s' % obj)
            self.instance.session.expunge_all()
            self.instance.session.close()
        except:
            self.instance.session.rollback()
            raise
        return obj

    @synchronized
    def remove(self, obj):
        try:
            logger.info('Removing Object: %s' % obj)
            self.instance.remove(obj)
            self.instance.session.commit()
            logger.debug('Removed Object: %s' % obj)
            self.instance.session.expunge_all()
            self.instance.session.close()
        except:
            self.instance.session.rollback()
            raise
        return obj

    @synchronized
    def update(self, obj):
        try:
            logger.info('Updating Object: %s' % obj)
            obj = self.instance.update(obj)
            self.instance.session.commit()
            logger.debug('Updated Object: %s' % obj)
            self.instance.session.expunge_all()
            self.instance.session.close()
        except:
            self.instance.session.rollback()
            raise
        return obj

    @synchronized
    def get_all(self, _class):
        try:
            logger.info('Get all of %s' % _class.__name__)
            lst = self.instance.get_all(_class)
            self.instance.session.commit()
        except:
            self.instance.session.rollback
            raise
        return lst

    @synchronized
    def get_by_id(self, _class, _id):
        try:
            logger.debug('Get by id %s of class %s' % (_id,_class.__name__))
            res = self.instance.get_by_id(_class, _id)
            self.instance.session.commit()
        except:
            self.instance.session.rollback
            raise
        return res

    @synchronized
    def get_by_name(self, _class, _name):
        try:
            logger.info('Get all of %s with name %s' % (_class.__name__ ,_name))
            res = self.instance.get_by_name(_class, _name)
            self.instance.session.commit()
        except:
            self.instance.session.rollback
            raise
        return res

    @synchronized
    def get_by_service_type(self, _class, _type):
        try:
            logger.info('Get all of %s with service_type %s' % (_class.__name__ ,_type))
            res = self.instance.get_by_service_type(_class, _type)
            self.instance.session.commit()
        except:
            self.instance.session.rollback
            raise
        return res

    def create_tables(self):
        Entities.create_tables(self.instance.engine)