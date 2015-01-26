__author__ = 'lto'


from abc import ABCMeta, abstractmethod


class RegisterAgent(object):
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
        print "ABC - Register.__init__()"

    @abstractmethod
    def register(self):
        """
        receive a register action
        :return:
        """
        print "ABC - RegisterAgent.register()"

    @abstractmethod
    def unregister(self):
        """
        Disposes an existing stack.
        :return:
        """
        print "ABC - RegisterAgent.unregister()"