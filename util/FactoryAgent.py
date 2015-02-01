__author__ = 'mpa'

import os
import logging

logger = logging.getLogger(__name__)

class FactoryAgent(object):

    @staticmethod
    def get_agent(agent, **kwargs):
        defs = agent.split('.')
        if len(defs) == 3:
            _package, _module, _class = defs
        else:
            raise ImportError('Wrong definition of the Class. Use \"package.module.class\".')
        try:
            _loaded_module = __import__(name='%s.%s' % (_package,_module), fromlist=[_module])
        except ImportError, exc:
            exc.message = 'FactoryAgent -> %s' % exc.message
            logger.exception(exc)
            raise ImportError(exc.message)
        try:
            _loaded_class = getattr(_loaded_module, _class)
        except AttributeError, exc:
            exc.message = 'FactoryAgent -> %s' % exc.message
            logger.exception(exc)
            raise AttributeError(exc.message)
        try:
            if len(kwargs) != 0:
                _instance = _loaded_class(**kwargs)
            else:
                _instance = _loaded_class()
        except TypeError, exc:
            needed_parameters = list(_loaded_class.__init__.func_code.co_varnames[1:_loaded_class.__init__.func_code.co_argcount])
            exc.message = 'FactoryAgent -> %s.%s. (args=%s)' % (_loaded_class.__name__,exc.message,needed_parameters)
            logger.exception(exc)
            raise TypeError(exc.message)
        return _instance