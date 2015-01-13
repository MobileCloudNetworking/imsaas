#   Copyright (c) 2014, Technische Universitaet Berlin
#   All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

__author__ = "tub"

from abc import ABCMeta, abstractmethod

class MonitoringAgent(object):
    """
    Wraps around the MaaS.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, endpoint):
        """
        Initializes helper for monitoring.

        :param endpoint: Optional maassm uri
        """
        pass

    @abstractmethod
    def deploy(self, token, tenant):
        """
        Request MaaS-so instantiation from SM and retrieve accessible address.

        :param token: a security token
        :param tenant: tenant name
        """
        raise NotImplementedError()

    @abstractmethod
    def address(self, token):
        """
        Returns MaaS_IP

        :param token: a security token
        """
        raise NotImplementedError()

    @abstractmethod
    def get_item(self, host, item, **kwargs):
        """
        Returns the last value of "item" from "host"

        :param host: hostname of itemholder
        :param item: itemname of wanted item
        :param kwargs: optional arguments
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def dispose(self, token):
        """
        Disposes monitoring helper and deployed monitoring-stack

        :param token: a security token
        """
        raise NotImplementedError()