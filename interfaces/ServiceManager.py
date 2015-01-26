__author__ = 'mpa'


from abc import ABCMeta, abstractmethod


class ServiceManager(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        """
        Initializes a new TopologyManager.
        :return:
        """
        print "ABC - TopologyManager.init()"

    @abstractmethod
    def create(self, config):
        """
        Creates a new Topology based on the config file.
        :return:
        """
        print "ABC - TopologyManager.create()"

    @abstractmethod
    def update(self):
        """
        Updates the current topology.
        :return:
        """
        print "ABC - TopologyManager.update()"