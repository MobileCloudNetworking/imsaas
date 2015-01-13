__author__ = 'mpa'


from abc import ABCMeta, abstractmethod


class RuntimeAgent(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        """
        Initializes a new RuntimeAgent.
        :return:
        """
        print "ABC - RuntimeAgent.init()"

    @abstractmethod
    def start(self, topology):
        """
        Starts a new Thread for the runtime observation.
        :return:
        """
        print "ABC - RuntimeAgent.run()"

    @abstractmethod
    def stop(self):
        """
        Starts a new Thread for the runtime observation.
        :return:
        """
        print "ABC - RuntimeAgent.delete(topology_id)"