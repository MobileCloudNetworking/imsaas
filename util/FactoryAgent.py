__author__ = 'mpa'

import os
import logging

module_name = 'services'
#PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
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