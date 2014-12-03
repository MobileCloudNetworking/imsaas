import logging
import threading
import time
from util.FactoryAgent import FactoryAgent
from util.SysUtil import SysUtil

__author__ = 'mpa'

from util.RuntimeAgent import RuntimeAgent as ABCRuntimeAgent

logger = logging.getLogger("EMMLogger")


class PolicyThread (threading.Thread):
    def __init__(self, threadID, policy, monitor, service_instance):
        super(PolicyThread, self).__init__()
        self._stop = threading.Event()
        self.threadID = threadID
        self.policy = policy
        self.monitor = monitor
        self.service_instance = service_instance

    def run(self):
        logger.debug("Starting " + self.threadID)
        self.active_policy()

    def active_policy(self):
        while True:
            for unit in self.service_instance.units:
                if self.check_alarm(unit, self.monitor):
                    logger.debug('Execute action' + self.policy.action)
                    time.sleep(self.policy.action.cooldown)
            time.sleep(self.policy.period)

    def check_alarm(self, unit, monitoring_service):
        alarm = self.policy.alarm
        item_value = monitoring_service.get_item(unit.ext_id, alarm.meter_name, {'period': alarm.evaluation_periods})
        if alarm.comparison_operator == '>' or alarm.comparison_operator == 'gt':
            if item_value > alarm.threshold:
                logger.debug('Trigger all the actions! ' + self.policy.actions)
                return True
        elif alarm.comparison_operator == '<' or alarm.comparison_operator == 'lt':
            if item_value < alarm.threshold:
                logger.debug('Trigger all the actions! ' + self.policy.actions)
                return True

        return False

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


class RuntimeAgent(ABCRuntimeAgent):

    def __init__(self):
        conf = SysUtil().get_sys_conf().props
        self.monitoring_service = FactoryAgent().get_agent(conf['monitoring'])
        self.topologies = {}

    def update(self):
        pass

    def run(self, topology):
        try:
            for service_instance in topology.service_instances:
                for policy in service_instance.policies:
                    th = PolicyThread(policy, self.monitoring_service, service_instance)
                    self.topologies[topology.id] = th
        except:
            logger.error("Error: unable to start thread that has to check policies")

    def delete(self, topology_id):
        self.topologies[topology_id].stop()
