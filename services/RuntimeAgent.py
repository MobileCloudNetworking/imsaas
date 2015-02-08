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


import logging
import threading
import time
from heatclient.exc import HTTPNotFound
from services.DatabaseManager import DatabaseManager
from core.TopologyOrchestrator import TopologyOrchestrator
from model.Entities import Unit
from interfaces.RuntimeAgent import RuntimeAgent as ABCRuntimeAgent
from util.FactoryAgent import FactoryAgent
from util.SysUtil import SysUtil, translate
import util.SysUtil as utilSys
from clients.heat import Client as HeatClient
from clients.neutron import Client as NeutronClient
from clients.nova import Client as NovaClient

from util.ImsDnsConfigurator import ImsDnsClient


__author__ = 'mpa'

logger = logging.getLogger(__name__)

HEAT_TO_EMM_STATE = {'CREATE_IN_PROGRESS': 'DEPLOYING',
                     'CREATE_COMPLETE': 'DEPLOYED',
                     'CREATE_FAILED': 'ERROR',
                     'DELETE_IN_PROGRESS': 'DELETING',
                     'DELETE_COMPLETE': 'DELETED',
                     'DELETE_FAILED': 'ERROR',
                     'UPDATE_IN_PROGRESS': 'UPDATING',
                     'UPDATE_COMPLETE': 'UPDATED',
                     'UPDATE_FAILED': 'ERROR',
                     'INIT_COMPLETE': 'INITIALISED',
                     'INIT_IN_PROGRESS': 'INITIALISING',
                     'INIT_FAILED': 'ERROR',
                     'ROLLBACK_COMPLETE': 'STATE_NOT_IMPLEMENTED',
                     'ROLLBACK_IN_PROGRESS': 'STATE_NOT_IMPLEMENTED',
                     'ROLLBACK_FAILED': ' STATE_NOT_IMPLEMENTED',
                     'SUSPEND_COMPLETE': 'STATE_NOT_IMPLEMENTED',
                     'SUSPEND_IN_PROGRESS': 'STATE_NOT_IMPLEMENTED',
                     'SUSPEND_FAILED': 'STATE_NOT_IMPLEMENTED',
                     'RESUME_COMPLETE': 'STATE_NOT_IMPLEMENTED',
                     'RESUME_IN_PROGRESS': 'STATE_NOT_IMPLEMENTED',
                     'RESUME_FAILED': 'STATE_NOT_IMPLEMENTED',
                     'ADOPT_COMPLETE': 'STATE_NOT_IMPLEMENTED',
                     'ADOPT_IN_PROGRESS': 'STATE_NOT_IMPLEMENTED',
                     'ADOPT_FAILED': 'STATE_NOT_IMPLEMENTED',
                     'SNAPSHOT_COMPLETE': 'STATE_NOT_IMPLEMENTED',
                     'SNAPSHOT_IN_PROGRESS': 'STATE_NOT_IMPLEMENTED',
                     'SNAPSHOT_FAILED': 'STATE_NOT_IMPLEMENTED',
                     'CHECK_COMPLETE': 'STATE_NOT_IMPLEMENTED',
                     'CHECK_IN_PROGRESS': 'STATE_NOT_IMPLEMENTED',
                     'CHECK_FAILED': 'STATE_NOT_IMPLEMENTED'
}


class RuntimeAgent(ABCRuntimeAgent):
    class __RuntimeAgent:

        def __init__(self):
            logger.debug("Starting RuntimeAgent.")
            # Get monitor name and service
            conf = SysUtil().get_sys_conf()
            monitor_name = conf.get('monitoring')
            self.monitoring_service = FactoryAgent.get_agent(monitor_name)
            self.policy_threads = {}
            self.heat_client = HeatClient()
            self.checker_threads = {}

        def __str__(self):
            return repr(self)

        def start(self, topology):
            #Start the monitoring agent
            self.monitoring_service.start()

            #Start CheckerThread the first time or update topology after restart
            if self.checker_threads.get(topology.id) is None:
                self.checker_threads[topology.id] = CheckerThread(topology)
                logger.debug("Starting CheckerThread")
                self.checker_threads[topology.id].start()
            else:
                self.checker_threads[topology.id].topology = topology

            #Start PolicyThreads if needed
            self.policy_threads[topology.id] = []
            try:
                for service_instance in topology.service_instances:
                    lock = threading.Lock()
                    for policy in service_instance.policies:
                        logger.debug('Creating new PolicyThread for %s' % policy)
                        _policy_thread = PolicyThread(topology=topology, runtime_agent=self, policy=policy,
                                                          service_instance=service_instance, lock=lock)
                        logger.debug('Created new PolicyThread for %s' % policy)
                        logger.debug("Starting PolicyThread for: %s" % service_instance.name)
                        _policy_thread.start()
                        logger.debug("Started PolicyThread for: %s" % service_instance.name)
                        self.policy_threads[topology.id].append(_policy_thread)
            except Exception as e:
                logger.warn("Error: unable to start thread that has to check policies. Message: " + e.message)
            logger.debug("All PolicyThreads %s" % self.policy_threads)

        def stop(self, _id):
            logger.debug("Stopping all PolicyThreads %s" % self.policy_threads[_id])
            for thread in self.policy_threads[_id]:
                logger.debug("Stopping PolicyThread %s" % thread)
                thread.stop()
            logger.debug("Stopped all PolicyThreads %s" % self.policy_threads[_id])
            logger.debug("Stopping CheckerThread: %s" % self.checker_threads[_id])
            #self.checker_threads[_id].stop()
            logger.debug("Stopped CheckerThread %s" % self.checker_threads[_id])

    instance = None

    def __init__(self):
        if not RuntimeAgent.instance:
            RuntimeAgent.instance = RuntimeAgent.__RuntimeAgent()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def start(self, topology):
        self.instance.start(topology)

    def stop(self, _id):
        self.instance.stop(_id)


class PolicyThread(threading.Thread):
    def __init__(self, topology,  runtime_agent, policy, service_instance, lock):
        super(PolicyThread, self).__init__()
        self.policy = policy
        self.service_instance = service_instance
        self.topology = topology

        self.runtime_agent = runtime_agent
        self.monitor = runtime_agent.monitoring_service
        self.lock = lock

        self.is_stopped = False
        conf = SysUtil().get_sys_conf()
        self.template_manager = FactoryAgent().get_agent(conf['template_manager'])
        self.db = FactoryAgent().get_agent(conf['database_manager'])
        self.heat_client = HeatClient()

    def run(self):
        logger.info("Initialise policy thread for policy %s" % self.policy.name)
        self.wait_until_final_state()
        logger.info("Starting policy thread for policy %s" % self.policy.name)
        if self.is_stopped:
            logger.info("Cannot start policy threads. PolicyThreads are stopped.")
        elif self.topology.state in ['DEPLOYED','UPDATED']:
            self.start_policy_checker_si()
            logger.info("Started policy thread for policy %s" % self.policy.name)
        else:
            logger.error(
                "ERROR: Something went wrong. Seems to be an error. Topology state -> %s. Didn't start the PolicyThread" % self.topology.state)


    def wait_until_final_state(self, final_states=[]):
        if len(final_states) == 0:
            final_states = ['DEPLOYED','UPDATED','ERROR','DELETED']
        units_count = 0
        for service_instance in self.topology.service_instances:
            units_count += len(service_instance.units)
        i = 0
        while not self.is_stopped and not self.topology.state in final_states and not i > units_count * 100:
            logger.debug('PolicyThread for %s -> Waiting 5 seconds' % self.policy.name)
            time.sleep(5)
            i += 1

    def active_policy_unit(self):
        logger.debug("Start active_policy check")
        while not self.is_stopped:
            logger.debug("Locking policy checking by %s" % self.policy.name)
            self.lock.acquire()
            for unit in self.service_instance.units:
                action = self.policy.action
                if action.scaling_adjustment > 0:
                    if (len(self.service_instance.units) + action.scaling_adjustment) > self.service_instance.size.get(
                            'max'):
                        logger.warning(
                            'Check upscaling - Maximum number of unit exceeded for service instance: %s' % self.service_instance.name)
                        break
                if action.scaling_adjustment < 0:
                    if (len(self.service_instance.units) + action.scaling_adjustment) < self.service_instance.size.get(
                            'min'):
                        logger.warning(
                            'Check downscaling - Minimum number of unit exceeded for service instance: %s' % self.service_instance.name)
                        break
                if self.service_instance.state != 'UPDATING' and self.check_alarm_unit(unit, self.monitor):
                    logger.debug('Execute action: %s' % repr(self.policy.action))
                    if action.adjustment_type == 'ChangeInCapacity':
                        self.service_instance.state = 'UPDATING'
                        self.topology.state = 'UPDATING'
                        if action.scaling_adjustment > 0:
                            if (len(
                                    self.service_instance.units) + action.scaling_adjustment) <= self.service_instance.size.get(
                                    'max'):
                                for i in range(action.scaling_adjustment):
                                    _hostname = '%s-%s' % (
                                        self.service_instance.name, str(len(self.service_instance.units) + 1))
                                    _state = 'Initialised'
                                    new_unit = Unit(hostname=_hostname, state=_state)
                                    self.service_instance.units.append(new_unit)
                            else:
                                logger.warning(
                                    'Maximum number of unit exceeded for service instance: %s' % self.service_instance.name)
                        else:
                            if (len(
                                    self.service_instance.units) + action.scaling_adjustment) >= self.service_instance.size.get(
                                    'min'):
                                for i in range(-action.scaling_adjustment):
                                    self.remove_unit(self.topology, self.service_instance)
                            else:
                                logger.warning(
                                    'Minimum number of unit exceeded for service instance: %s' % self.service_instance.name)
                        try:
                            self.db.update(self.topology)
                        except Exception, msg:
                            logger.error(msg)
                            self.topology.state='ERROR'
                            self.topology.ext_id = None
                        template = self.template_manager.get_template(self.topology)
                        # logger.debug("Send update to heat template with: \n%s" % template)
                        self.heat_client.update(stack_id=self.topology.ext_id, template=template)
                    logger.info('Sleeping (cooldown) for %s seconds' % self.policy.action.cooldown)
                    time.sleep(self.policy.action.cooldown)
            logger.debug("Release Policy lock by %s" % self.policy.name)
            self.lock.release()
            logger.info('Sleeping (evaluation period) for %s seconds' % self.policy.period)
            time.sleep(self.policy.period)

    def check_alarm_unit(self, unit, monitoring_service):
        logger.debug("checking for alarms")
        alarm = self.policy.alarm
        logger.debug("request item value: %s" % unit.hostname)
        item_value = monitoring_service.get_item(res_id=unit.ext_id, item_name=alarm.meter_name,
                                                 kwargs={'period': alarm.evaluation_periods})
        # item_value = 50
        logger.debug("received item value: %s" % item_value)
        if alarm.comparison_operator == '>' or alarm.comparison_operator == 'gt':
            logger.debug("Check upscaling: check that item value is bigger than threshold")
            if item_value > alarm.threshold:
                logger.info('Trigger the action: %s' % repr(self.policy.action))
                return True
            else:
                logger.debug("Check upscaling: item value is lower than threshold")
        elif alarm.comparison_operator == '<' or alarm.comparison_operator == 'lt':
            logger.debug("Check downscaling: check that item value is lower than threshold")
            if item_value < alarm.threshold:
                logger.info('Trigger the action: %s' % repr(self.policy.action))
                return True
            else:
                logger.debug("Check downscaling: item value is bigger than threshold")
        logger.debug("Check item values finished")
        return False

    def start_policy_checker_si(self):
        logger.debug("Start active_policy check for policy %s on service instance %s" % (
            self.policy.name, self.service_instance.name))
        while not self.is_stopped:
            logger.debug("Locking policy checking from %s" % self.policy.name)
            self.lock.acquire()
            logger.debug("Locked policy checking from %s" % self.policy.name)
            action = self.policy.action
            if action.scaling_adjustment > 0:
                if (len(self.service_instance.units) + action.scaling_adjustment) > self.service_instance.size.get(
                        'max'):
                    logger.warning(
                        'Check upscaling - Maximum number of unit exceeded for service instance: %s' % self.service_instance.name)
                    logger.debug("Release Policy lock by %s" % self.policy.name)
                    self.lock.release()
                    time.sleep(self.policy.period)
                    continue
            if action.scaling_adjustment < 0:
                if (len(self.service_instance.units) + action.scaling_adjustment) < self.service_instance.size.get(
                        'min'):
                    logger.warning(
                        'Check downscaling - Minimum number of unit exceeded for service instance: %s' % self.service_instance.name)
                    logger.debug("Release Policy lock by %s" % self.policy.name)
                    self.lock.release()
                    time.sleep(self.policy.period)
                    continue
            if self.service_instance.state != 'UPDATING' and self.check_alarm_si():
                logger.debug('Execute action: %s' % repr(self.policy.action))
                if action.adjustment_type == 'ChangeInCapacity':
                    self.service_instance.state = 'UPDATING'
                    self.topology.state = 'UPDATING'
                    if action.scaling_adjustment > 0:
                        if (len(
                                self.service_instance.units) + action.scaling_adjustment) <= self.service_instance.size.get(
                                'max'):
                            for i in range(action.scaling_adjustment):
                                _hostname = '%s-%s' % (
                                    self.service_instance.name, str(len(self.service_instance.units) + 1))
                                _state = 'DEFINED'
                                new_unit = Unit(hostname=_hostname, state=_state)
                                new_unit.service_instance_id = self.service_instance.id
                                self.service_instance.units.append(new_unit)
                                self.db.persist(new_unit)
                        else:
                            logger.warning(
                                'Maximum number of unit exceeded for service instance: %s' % self.service_instance.name)
                    else:
                        if (len(
                                self.service_instance.units) + action.scaling_adjustment) >= self.service_instance.size.get(
                                'min'):
                            for i in range(-action.scaling_adjustment):
                                removed_unit = self.remove_unit(self.topology, self.service_instance)
                                self.db.remove(removed_unit)
                        else:
                            logger.warning(
                                'Minimum number of unit exceeded for service instance: %s' % self.service_instance.name)
                    topology = self.db.update(self.topology)
                    template = self.template_manager.get_template(self.topology)
                    # logger.debug("Send update to heat template with: \n%s" % template)
                    try:
                        self.heat_client.update(stack_id=self.topology.ext_id, template=template)
                        self.wait_until_final_state()
                        if not self.topology.state == 'DEPLOYED':
                            logger.error(
                                "ERROR: Something went wrong. Seems to be an error. Topology state -> %s" % self.topology.state)
                            self.lock.release()
                            return
                    except:
                        self.is_stopped = True
                        self.lock.release()
                logger.info('Sleeping (cooldown) for %s seconds' % self.policy.action.cooldown)
                time.sleep(self.policy.action.cooldown)
            logger.debug("Release Policy lock from %s" % self.policy.name)
            self.lock.release()
            logger.info('Sleeping (evaluation period) for %s seconds' % self.policy.period)
            time.sleep(self.policy.period)

    def check_alarm_si(self):
        logger.debug("Checking for alarms on service instance %s" % self.service_instance.name)
        alarm = self.policy.alarm
        logger.debug("Monitoring service: %s" % self.monitor)
        _sum = 0
        _units_count = 0
        si_avg = None
        logger.debug("Requesting meter values for service instance: %s" % self.service_instance.name)
        for unit in self.service_instance.units:
            logger.debug("Requesting meter value for unit with hostname %s, item_name %s, and period: %s" %(unit.hostname,alarm.meter_name,alarm.evaluation_periods))
            item_value = self.monitor.get_item(res_id=unit.hostname, item_name=alarm.meter_name, kwargs={'period': alarm.evaluation_periods})
            logger.debug("Got item value for %s -> %s" % (unit.hostname, item_value))
            if item_value:
                _sum += item_value
                _units_count += 1
            else:
                _sum = -1
                _units_count = -1
                return False
        if _sum >= 0 and _units_count > 0:
            si_avg = _sum / _units_count
            logger.debug("Average item value for the whole service instance group: %s -> %s" % (
                self.service_instance.name, si_avg))
        if not si_avg or si_avg < 0:
            logger.warning(
                "Average item value for the whole service instance group %s was not calculated. Any Problems?" % (
                    self.service_instance.name))
            return False
        # item_value = 50
        if alarm.comparison_operator == '>' or alarm.comparison_operator == 'gt':
            logger.debug(
                "Check upscaling: is the avg meter value bigger than threshold for service instance %s?" % self.service_instance.name)
            if si_avg > alarm.threshold:
                logger.debug(
                    "Check upscaling: avg item value is bigger than threshold for service instance %s." % self.service_instance.name)
                logger.info('Trigger the action: %s' % repr(self.policy.action))
                return True
            else:
                logger.debug(
                    "Check upscaling: avg item value is lower than threshold for service instance %s." % self.service_instance.name)
        elif alarm.comparison_operator == '<' or alarm.comparison_operator == 'lt':
            logger.debug(
                "Check downscaling: is the avg meter value lower than threshold for service instance %s." % self.service_instance.name)
            if si_avg < alarm.threshold:
                logger.debug(
                    "Check downscaling: item value is lower than threshold for service instance %s." % self.service_instance.name)
                logger.info('Trigger the action: %s' % repr(self.policy.action))
                return True
            else:
                logger.debug(
                    "Check downscaling: item value is bigger than threshold for service instance %s." % self.service_instance.name)
        logger.debug(
            "Checking meter values are finished for service instance %s. Alarm was not triggered." % self.service_instance.name)
        return False

    def remove_unit(self, topology, service_instance):
        removed_unit = service_instance.units.pop(len(service_instance.units) - 1)
        return removed_unit

    def stop(self):
        self.is_stopped = True

    def stopped(self):
        return self._stop.isSet()


class CheckerThread(threading.Thread):
    def __init__(self, topology):
        super(CheckerThread, self).__init__()
        self.heatclient = HeatClient()
        self.topology = topology
        self.db = DatabaseManager()
        self.is_stopped = False
        self.is_dns_configured = False
        self.novac = NovaClient()
        self.dns_configurator = ImsDnsClient()
        self.neutronc = NeutronClient(utilSys.get_endpoint('network'), utilSys.get_token())

    def run(self):
        while not self.is_stopped:
            self.update_topology_state()
            if self.topology.state == 'DELETED':
                TopologyOrchestrator.delete(self.topology)
                self.is_stopped = True
            for si in self.topology.service_instances:
                if not self.is_stopped:
                    for unit in si.units:
                        if len(unit.ports) == 0:
                            self.set_ips(unit)
            if self.topology.state == 'DEPLOYED' and not self.is_dns_configured:
                self.configure_dns()
                self.is_dns_configured = True
            time.sleep(30)

    def configure_dns(self):
        for si in self.topology.service_instances:
            for unit in si.units:
                self.dns_configurator.configure_dns_entry(si.service_type, unit.hostname)(unit.ips['mgmt'])

    def print_test(self, ip):
        logging.debug("Testing dns entry for test service with ip %s"%ip)



    def set_ips(self, unit):
        # Retrieving ports and ips information
        if not self.topology.state == 'ERROR':
            logger.debug('Setting ips for unit %s.' % unit.hostname)
        if not self.topology.state == 'ERROR' and unit.ext_id:
            self.novac.set_ips(unit)
            self.db.update(unit)
            ports = self.neutronc.get_ports(unit)
            for port in ports:
                port.unit_id = unit.id
                self.db.persist(port)
            unit.ports = ports
            self.db.update(unit)
            logger.debug("Ports: ")
            for port in unit.ports:
                logger.debug(port)
        return unit

    def stop(self):
        self.is_stopped = True

    def update_topology_state(self):
        #get stack details and set the topology state
        try:
            stack_details = self.heatclient.show(stack_id=self.topology.ext_id)
            logger.debug('Stack details of %s: %s' % (self.topology.ext_name, stack_details))
            old_state = self.topology.state
            old_detailed_state = self.topology.detailed_state
            if stack_details:
                self.topology.state = translate(stack_details.get('stack_status'), HEAT_TO_EMM_STATE)
                self.topology.detailed_state = stack_details.get('stack_status_reason')
            if old_state != self.topology.state or old_detailed_state != self.topology.detailed_state:
                self.db.update(self.topology)
        except Exception, exc:
            logger.exception(exc)
            self.topology.state='ERROR'
            raise

        #Get details of resources and update state for each of them
        try:
            resource_details = self.heatclient.list_resources(self.topology.ext_id)
            logger.debug('Resource details of %s: %s' % (self.topology.ext_name, resource_details))
        except HTTPNotFound, exc:
            self.topology.state='DELETED'
            return
        except Exception, exc:
            logger.exception(exc)
            self.topology.state='ERROR'

        #Update all service instance state down to all units
        for service_instance in self.topology.service_instances:
            self.update_service_instance_state(service_instance=service_instance, resource_details=resource_details)

        #Check topology state again and check also all service instances
        all_completed = False
        if self.topology.state in ['DEPLOYED', 'UPDATED']:
            topology_completed = True
        else:
            topology_completed = False
        #Assume that the topology deployment is completed
        all_completed = topology_completed
        #Check if there are any errors downstairs
        for service_instance in self.topology.service_instances:
            if service_instance.state in ['DEPLOYED', 'UPDATED']:
                si_completed = True
            elif service_instance.state == 'ERROR':
                si_completed = False
                self.topology.state = 'ERROR'
            else:
                si_completed = False
                self.topology.state = service_instance.state
            all_completed = all_completed and si_completed
        if all_completed:
            self.topology.state = 'DEPLOYED'
        if old_state != self.topology.state:
            self.db.update(self.topology)

    def update_service_instance_state(self, service_instance, resource_details=None):
        old_state = service_instance.state
        if not resource_details:
            try:
                resource_details = self.heatclient.list_resources(self.topology.ext_id)
                logger.debug('Resource details of %s: %s' % (self.topology.ext_name, resource_details))
            except HTTPNotFound, exc:
                self.topology.state='DELETED'
                return
            except Exception, exc:
                logger.exception(exc)
                self.topology.state='ERROR'
        #Update all unit states
        for unit in service_instance.units:
            self.update_unit_state(unit, resource_details)

        # Update state of service instance
        si_completed = True
        is_updated = False
        for unit in service_instance.units:
            if unit.state == 'INITIALISING':
                if service_instance.state == 'DEFINED':
                    service_instance.state = unit.state
                unit_completed = False
            elif unit.state in ['DEPLOYING','UPDATING']:
                service_instance.state = unit.state
                unit_completed = False
            elif unit.state == 'DEPLOYED':
                unit_completed = True
            elif unit.state == 'UPDATED':
                unit_completed = True
                is_updated = True
            elif unit.state == 'ERROR':
                service_instance.state = 'ERROR'
                unit_completed = False
            else:
                unit_completed = False
            si_completed = si_completed and unit_completed
        if si_completed:
            if is_updated:
                service_instance.state = 'UPDATED'
            else:
                service_instance.state = 'DEPLOYED'

        #Update only when the state is changed
        if old_state != service_instance.state:
            self.db.update(service_instance)

    def update_unit_state(self, unit, resource_details=None):
        if not resource_details:
            try:
                resource_details = self.heatclient.list_resources(self.topology.ext_id)
                logger.debug('Resource details of %s: %s' % (self.topology.ext_name, resource_details))
            except HTTPNotFound, exc:
                self.topology.state='DELETED'
                return
            except Exception, exc:
                logger.exception(exc)
                self.topology.state='ERROR'
        for vm in resource_details:
            if vm.get('resource_type') == "OS::Nova::Server":
                if vm.get('resource_name') == unit.hostname:
                    unit.ext_id = vm['physical_resource_id']
                    heat_state = vm.get('resource_status')
                    if heat_state:
                        _new_state = translate(heat_state, HEAT_TO_EMM_STATE)
                        logger.debug("State of unit %s: translate from %s to %s" % (unit.hostname, heat_state, _new_state))
                        if _new_state != unit.state:
                            unit.state = _new_state
                            self.db.update(unit)
                    else:
                        logger.warning("State of unit %s: %s" % (unit.hostname, vm.get('resource_status')))
                        raise Exception