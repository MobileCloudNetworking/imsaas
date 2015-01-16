import logging
import threading
from interfaces.RegisterAgent import RegisterAgent as ABCRegisterAgent
from model.Entities import Topology
from msg_utils.MessagingEntities import RegisterUnitMessage
from services.DatabaseManager import DatabaseManager
from services.Register import Register
from msg_utils.zeromq_agent import Subscriber

__author__ = 'lto'


logger = logging.getLogger("EMMLogger")


def check_units_ws(units):
    for unit in units:
        if not unit.ws:
            return False
    return True


class ZeroMQRegisterAgent(ABCRegisterAgent, threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.reg = Register()
        self.subscriber = Subscriber(filter='EMM')
        self.stop = False
        self.db = DatabaseManager()

    def unregister(self, unit, ws):
        self.reg.unregister_unit(unit, ws)

    def register(self, unit, ws):
        self.reg.register_unit(unit, ws)

    def run(self):
        logger.debug("Starting RegisterAgent")
        while not self.stop:
            msg = self.subscriber.receive(cls_message=RegisterUnitMessage)
            logger.debug("Received %s" % msg)
            topologies = self.db.get_all(Topology)
            logger.debug("Looking on %s topologies" % len(topologies))
            for top in topologies:
                for si in top.service_instances:
                    if si.service_type == 'MediaServer':
                        for unit in si.units:
                            if unit.hostname == msg.hostname:
                                self.register(unit=unit, ws=msg.ws)
                                logger.info("Registered unit %s" % unit)
                                break
                        self.stop = check_units_ws(si.units)
                        if self.stop:
                            break
                if self.stop:
                    break
