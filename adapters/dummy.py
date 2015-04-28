__author__ = 'gca'


from interfaces.ServiceAdapter import ServiceAdapter as ABCServiceAdapter
import httplib2


class DummyAdapter(ABCServiceAdapter):

    def __init__(self):
        """
        Initializes a new ServiceAdapter.
        :return:
        """
        pass

    def preinit(self, config):
        """
        Creates a new Service based on the config file.
        :return:
        """
        print "I'm the dummy adapter, preinit dummy service, received config %s" %config

    def install(self, config):
        """
        Creates a new Service based on the config file.
        :return:
        """
        print "I'm the dummy adapter, installing dummy service, received config %s" %config

    def add_dependency(self, config, ext_service):
        """
        Add the dependency between this service and the external one
        :return:
        """
        print "I'm the dummy adapter, installing dummy service, received config %s" %config

    def remove_dependency(self, config, ext_service):
        """
        Remove the dependency between this service and the external one
        :return:
        """
        pass

    def terminate(self):
        """
        Terminate the service
        :return:
        """
        pass
