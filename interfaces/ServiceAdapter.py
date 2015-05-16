__author__ = 'gca'


from abc import ABCMeta, abstractmethod


class ServiceAdapter(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        """
        Initializes a new ServiceAdapter.
        :return:
        """
        print "ABC - ServiceAdapter.init()"


    @abstractmethod
    def install(self, config):
        """
        Creates a new Service based on the config file.
        :return:
        """
        print "ABC - ServiceAdatper.preinit()"

    @abstractmethod
    def install(self, config):
        """
        Creates a new Service based on the config file.
        :return:
        """
        print "ABC - ServiceAdatper.install()"

    @abstractmethod
    def add_dependency(self, config, ext_unit, ext_service):
        """
        Add the dependency between this service and the external one
        :return:
        """
        print "ABC - ServiceAdatper.add_dependency()"

    @abstractmethod
    def pre_start(self, config):
        """
        start a service instance
        :return:
        """
        print "ABC - ServiceAdatper.preStart()"

    @abstractmethod
    def start(self, config ):
        """
        start a service instance
        :return:
        """
        print "ABC - ServiceAdatper.start()"

    @abstractmethod
    def remove_dependency(self, config, ext_unit, ext_service):
        """
        Remove the dependency between this service and the external one
        :return:
        """
        print "ABC - ServiceAdatper.remove_dependency()"

    @abstractmethod
    def terminate(self):
        """
        Terminate the service
        :return:
        """
        print "ABC - ServiceAdatper.terminate()"