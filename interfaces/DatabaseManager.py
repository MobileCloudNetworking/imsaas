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


__author__ = 'mpa'


from abc import ABCMeta, abstractmethod


class DatabaseManager(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        """
        Initializes a new DatabaseManager.
        :return:
        """
        print "ABC - DatabaseManager.init()"

    @abstractmethod
    def persist(self, obj):
        """
        Prsist a new Object in the database.
        :return:
        """
        print "ABC - DatabaseManager.persist(obj)"


    @abstractmethod
    def remove(self, obj):
        """
        Remove an object from the database.
        :return:
        """
        print "ABC - DatabaseManager.remove(obj)"

    @abstractmethod
    def update(self, obj):
        """
        Update an object from the database.
        :return:
        """
        print "ABC - DatabaseManager.update(obj)"


    @abstractmethod
    def get_all(self, _class):
        """
        Update an object from the database.
        :return:
        """
        print "ABC - DatabaseManager.get_all(class)"


    @abstractmethod
    def get_by_id(self, _class, _id):
        """
        Update an object from the database.
        :return:
        """
        print "ABC - DatabaseManager.get_by_id(class, id)"


    @abstractmethod
    def get_by_name(self, _class, _name):
        """
        Update an object from the database.
        :return:
        """
        print "ABC - DatabaseManager.get_by_name(class, name)"

    @abstractmethod
    def get_by_service_type(self, _class, _type):
        """
        Update an object from the database.
        :return:
        """
        print "ABC - DatabaseManager.get_by_name(class, name)"