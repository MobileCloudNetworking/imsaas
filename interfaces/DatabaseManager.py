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