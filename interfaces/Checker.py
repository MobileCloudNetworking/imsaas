__author__ = 'mpa'

from abc import ABCMeta, abstractmethod


class Checker:
    __metaclass__ = ABCMeta

    @staticmethod
    @abstractmethod
    def check(action=None, alarm=None, flavor=None, image=None, key=None, network=None, policy=None,
              security_group=None, service=None, service_instance=None, service_type=None, topology=None, unit=None):
        """
        Check given resource..
        :return:
        """
        print "ABC - Checker.check()"