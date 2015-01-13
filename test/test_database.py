import logging
import os

from model.Entities import Topology, ServiceInstance, Command, Unit
from services import DatabaseManager
from util.SysUtil import SysUtil

PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

__author__ = 'lto'

if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s_%(process)d:%(pathname)s:%(lineno)d [%(levelname)s] %(message)s',level=logging.DEBUG)
    logger = logging.getLogger("EMMLogger")
    handler = logging.FileHandler('%s/logs/%s.log' % (PATH, os.path.basename(__file__)))
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s_%(process)d:%(pathname)s:%(lineno)d [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    db = DatabaseManager.DatabaseManager()

    for u in db.get_all(Unit):
        logger.debug(u.ips)
        logger.debug(u.floating_ips)
        logger.debug(u.ports)
    # top = Topology()
    # top.name = 'top1'
    # top.state = 'Initialised'
    # top.service_instances = []
    #
    # serv = ServiceInstance()
    # serv.state = 'Initialised'
    # serv.flavor = 'm1.small'
    # serv.name = 'Serv1'
    # c = Command('user_data')
    # serv.user_data.append(c)
    # serv.image = "image_id"
    #
    # top.service_instances.append(serv)
    #
    # db.persist(top)
    #
    # for top1 in db.get_all(Topology):
    #     logger.debug(top1.name)
    #
    # logger.debug(top.id)
    #
    # try:
    #     top2 = db.get_by_id(Topology, top.id)
    # except NotFoundException as e:
    #     logger.error(e.message)
    #     exit(1)
    #
    # logger.debug(str(top2))
    #
    # db.remove(top)
    #
    # logger.debug(len(db.get_all(Topology)))