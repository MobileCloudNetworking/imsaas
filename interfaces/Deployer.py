__author__ = 'mpa'


from abc import ABCMeta, abstractmethod


class Deployer(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        """
        Initializes a new Deployer.
        :param tenant_name:
        :param username:
        :param password:
        :param auth_url:
        :return:
        """
        print "ABC - Deployer.__init__()"

    @abstractmethod
    def deploy(self, topology):
        """
        Deploys a new stack.
        :return:
        """
        print "ABC - Deployer.deploy()"

    @abstractmethod
    def dispose(self):
        """
        Disposes an existing stack.
        :return:
        """
        print "ABC - Deployer.dispose()"