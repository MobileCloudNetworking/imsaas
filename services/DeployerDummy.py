import threading
import time

from interfaces.Deployer import Deployer as ABCDeployer

from services import TemplateManager
from util.FactoryAgent import FactoryAgent
from util.SysUtil import SysUtil


__author__ = 'mpa'

import logging

logger = logging.getLogger(__name__)


class DeployerDummy(ABCDeployer):

    def __init__(self):
        # self.heatclient = HeatClient()
        conf = SysUtil().get_sys_conf()
        self.template_manager = FactoryAgent().get_agent(conf['template_manager'])
        self.db = FactoryAgent().get_agent(conf['database_manager'])
        self.runtime_agent = FactoryAgent().get_agent(conf['runtime_agent'])

        #self.reg = FactoryAgent().get_agent(file_name=conf['register_agent_file'],
        #                                    class_name=conf['register_agent_class'])
        pass

    def deploy(self, topology):
        logger.debug("Start Deploying")
        name = topology.name
        template = self.template_manager.get_template(topology)
        logger.debug("stack name: %s" % name)
        logger.debug("template: %s" % template)
        try:
            # stack_id = stack_details['stack']['id']
            stack_details = StackDetails()
            stack_details.id = 'dummy-id'
            """
            filling the topology with real values
            """
            # res = self.heatclient.list_resources(stack_id)
            for service_instance in topology.service_instances:
                for unit in service_instance.units:
                    unit.ext_id = unit.id
            topology.ext_id = 1
            logger.debug("stack id: dummy-id")
        except KeyError, exc:
            logger.error(KeyError)
            logger.error(exc)
            stack_id = "None"

        self.runtime_agent.start(topology)

        return stack_details

    def dispose(self, topology):
        # try:
        #     self.db.remove(topology)
        # except:
        pass
            # stack_details = self.heatclient.delete(stack_id)
            # logger.debug("stack details after delete: %s" % stack_details)
            # return stack_details

    def details(self, topology_id):
        logger.debug("Stack actually running dummy-id")
        return "dummy-id"


class CheckerThread(threading.Thread):
    def __init__(self, topology, heat_client, stack_id):
        super(CheckerThread, self).__init__()
        self._stop = threading.Event()
        self.topology = topology
        self.heat_client = heat_client
        self.stack_id = stack_id

    def run(self):
        logger.debug("Starting new thread")
        i = 0
        while i < 18:
            for service_instance in self.topology.service_instances:
                for unit in service_instance.units:
                    if i == 0:
                        unit.state = 'Initialised'
                    else:
                        unit.state = 'Started'
                        dbm_name = SysUtil().get_sys_conf()['database_manager']
                        db = FactoryAgent.get_agent(dbm_name)
                        db.update(unit)
                        # conf = SysUtil().get_sys_conf().props
                        # runtime_agent = FactoryAgent().get_agent(conf['runtime_agent'])
                        # runtime_agent.run(self.topology)
                if i > 1:
                    return
            time.sleep(2)
            i += 1
        logger.error("Can't get info on the units after 180 seconds, is there a problem?")

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


class StackDetails():
    pass