from abc import ABCMeta, abstractmethod

__author__ = 'beb'


class ConnectivityManager(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        """
        Initializes a new ConnectivityManager.
        :return:
        """
        print "ABC - ConnectivityManager.init()"

    @abstractmethod
    def set_host(self, topology):
        """
        Sets the host that each individual unit will be deployed on.
        :return:
        """
        print "ABC - ConnectivityManager.set_host(topology)"

    @abstractmethod
    def set_qos(self, topology):
        """
        Enables QoS for individual units.
        :return:
        """
        print "ABC - ConnectivityManager.set_qos(topology)"