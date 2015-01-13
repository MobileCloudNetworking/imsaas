import os
from util.SysUtil import SysUtil
import logging


__author__ = 'lto'

PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s_%(process)d:%(pathname)s:%(lineno)d [%(levelname)s] %(message)s',level=logging.DEBUG)
    logger = logging.getLogger("EMMLogger")
    handler = logging.FileHandler('%s/logs/%s.log' % (PATH, os.path.basename(__file__)))
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s_%(process)d:%(pathname)s:%(lineno)d [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    sys_util = SysUtil()
    sys_util.init_sys()

    print sys_util.get_sys_conf().props;