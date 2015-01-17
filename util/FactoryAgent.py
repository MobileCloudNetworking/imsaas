# Copyright 2014 Technische Universitaet Berlin
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import os
import logging

__author__ = 'mpa'

module_name = 'services'
PATH = os.environ.get('OPENSHIFT_REPO_DIR', '.')


logger = logging.getLogger('EMMLogger')


class FactoryAgent(object):

    @staticmethod
    def get_agent(file_name, **kwargs):
        logger.info("getting agent %s" %file_name)
        for py in [f[:-3] for f in os.listdir(PATH + '/' + module_name) if f.endswith('.py') and f != '__init__.py']:
            if py == file_name:
                logger.debug("importing module %s in path %s " %(py,PATH))
                module = __import__(module_name + '.' + py)
                try:
                    class_ = getattr(module, file_name).__getattribute__(file_name)
                    if len(kwargs) != 0:
                        instance = class_(kwargs)
                    else:
                        instance = class_()
                    return instance
                except AttributeError as e:
                    logger.error(e)
                    continue
        raise AttributeError('Class ' + file_name + ' not in the ' + module_name + ' folder')