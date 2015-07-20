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



__author__ = 'mpa'

from interfaces.Checker import Checker as ABCChecker
import logging
import re
import traceback

from services.DatabaseManager import DatabaseManager
from model.Entities import Topology, Service, Network, SecurityGroup, Image, Flavor, Key
from emm_exceptions.NotFoundException import NotFoundException
from emm_exceptions.InvalidInputException import InvalidInputException
from emm_exceptions.TypeErrorException import TypeErrorException
from emm_exceptions.NotDefinedException import NotDefinedException
from emm_exceptions.NotUniqueException import NotUniqueException


logger = logging.getLogger(__name__)

# alarms
METERS = ["system.cpu.util[,idle]"]
STATISTICS = ["avg"]
COMPARISON_OPERATORS = ["gt", "lt", "<", ">"]
# actions
ADJUSTMENT_TYPES = ["ChangeInCapacity"]
# security rules
PROTOCOLS = ["tcp", "udp", "icmp"]
# requirements
PARAMETERS = ["private_ip", "public_ip"]

class Checker(ABCChecker):

    @staticmethod
    def check(action=None, alarm=None, flavor=None, image=None, key=None, network=None, policy=None, security_group=None,
              service=None, service_instance=None, service_type=None, topology=None, unit=None):
        try:
            if action:
                checkAction(action)
            if alarm:
                checkAlarm(alarm)
            if flavor:
                checkFlavor(flavor)
            if image:
                checkImage(image)
            if key:
                checkKey(key)
            if network:
                checkNetwork(network)
            if policy:
                checkPolicy(policy)
            if security_group:
                checkSecurityGroupUniqueness(security_group)
                checkSecurityGroup(security_group)
            if service:
                checkServiceUniqueness(service)
                checkService(service)
            if service_instance:
                checkServiceInstance(service_instance)
            if service_type:
                checkServiceType(service_type)
            if topology:
                checkTopolgoyUniqueness(topology)
                checkTopology(topology)
            if unit:
                checkUnit(unit)
        except Exception, exc:
            logger.exception(exc)
            raise


def checkTopology(topology):
    logger.info("Check topology \"%s\"." % topology.name)
    # check service instances
    logger.debug("Check service_instances of topology %s." % topology.name)
    try:
        for service_instance in topology.service_instances:
            # check service instance uniqueness inside topology
            logger.debug(
                "Check service instance's uniqueness of \"%s\" of topology \"%s\"." % (
                service_instance.name, topology.name))
            checkServiceInstanceUniqueness(service_instance, topology)
            # check service instance except requirements
            logger.debug("Check service instance \"%s\" of topology \"%s\"." % (service_instance.name, topology.name))
            checkServiceInstance(service_instance)
            # check requirements
            logger.debug("Check requirements' uniqueness for service instance \"%s\" of topology \"%s\"." % (
                service_instance.name, topology.name))
            checkRequirementsUniqueness(service_instance.requirements)
            logger.debug("Check requirements' dependencies for service instance \"%s\" of topology \"%s\"." % (
                service_instance.name, topology.name))
            checkRequirementsDependencies(service_instance.requirements, topology.service_instances)
            logger.debug("Check policies' uniqueness for service instance \"%s\" of topology \"%s\"." % (
                service_instance.name, topology.name))
            checkPoliciesUnqiueness(service_instance.policies)
    except Exception, exc:
        exc.message = 'Topology:\"%s\"->%s' % (topology.name, exc.message)
        raise exc
    logger.info("Topology \"%s\" is valid" % topology.name)


def checkTopolgoyUniqueness(topology):
    db = DatabaseManager()
    # check names
    logger.debug("Check uniqueness of name of the toplogy \"%s\"." % topology.name)
    for top in db.get_all(Topology):
        if topology.ext_name == top.ext_name and topology.id != top.id:
            raise NotUniqueException("Topology name \"%s\" is already used." % topology.name)


def checkServiceInstance(service_instance):
    # check service type
    logger.debug("Check service_type of service instance \"%s\"." % service_instance.name)
    try:
        if service_instance.service_type:
            checkServiceType(service_instance.service_type)
        else:
            raise NotDefinedException("service_type is not defined.")

        # check flavor
        logger.debug("Check flavor of service instance \"%s\"." % service_instance.name)
        if service_instance.flavor:
            checkFlavor(service_instance.flavor)
        else:
            raise NotDefinedException("flavor is not defined.")

        # check image
        logger.debug("Check image of service instance \"%s\"." % service_instance.name)
        if service_instance.image:
            checkImage(service_instance.image)
        else:
            raise NotDefinedException("image is not defined.")

        # check keypair if provided
        logger.debug("Check key of service instance \"%s\"." % service_instance.name)
        if service_instance.key:
            checkKey(service_instance.key)

        # check size
        logger.debug("Check size of service instance \"%s\"." % service_instance.name)
        if service_instance.size:
            checkSize(service_instance.size)
        else:
            raise NotDefinedException("size is not defined.")

        # check networks
        logger.debug("Check networks of service instance \"%s\"." % service_instance.name)
        for network in service_instance.networks:
            checkNetwork(network)

        # check policies
        if service_instance.policies:
            logger.debug("Check policies of service instance \"%s\"." % service_instance.name)
            for policy in service_instance.policies:
                checkPolicy(policy)
            logger.debug("Check uniqueness of policies for service instance \"%s\"." % service_instance.name)
            checkPoliciesUnqiueness(service_instance.policies)

        # check requirements
        if service_instance.requirements:
            logger.debug("Check requirements of service instance \"%s\"." % service_instance.name)
            for requirement in service_instance.requirements:
                checkRequirement(requirement)
    except Exception, exc:
        exc.message = 'ServiceInstance:\"%s\"->%s' % (service_instance.name, exc.message)
        raise exc


def checkServiceInstanceUniqueness(service_instance, topology):
    for comp_service_instance in topology.service_instances:
        try:
            if service_instance.name == comp_service_instance.name and service_instance != comp_service_instance:
                raise NotUniqueException("name:\"%s\" is not unique." % service_instance.name)
        except Exception, exc:
            exc.message = '%s->%s' % (service_instance.name, exc.message)
            raise exc
    logger.debug("name \"%s\" of serivce instance is unique." % service_instance.name)


def checkUnit(unit):
    pass


def checkPolicy(policy):
    try:
        if policy.name:
            logger.debug("Check policy \"%s\"" % policy.name)
        else:
            raise NotDefinedException("name is not defined.")
        if policy.period:
            if isinstance(policy.period, (long, int)):
                if policy.period > 0:
                    logger.debug("period \"%s\" is valid." % (policy.period))
                else:
                    raise InvalidInputException(
                        "period:\"%s\" is not valid. Value must be greater than 0." % policy.period)
            else:
                raise InvalidInputException("period:\"%s\" is not valid. It must be an integer." % policy.period)
        else:
            raise NotDefinedException("period is not defined." % policy.name)
        if policy.alarm:
            logger.debug("Check alarm of policy \"%s\"" % policy.name)
            checkAlarm(policy.alarm)
        else:
            raise NotDefinedException("alarm is not defined.")
        if policy.action:
            logger.debug("Check action of policy \"%s\"" % policy.name)
            checkAction(policy.action)
        else:
            raise NotDefinedException("action is not defined.")
    except Exception, exc:
        exc.message = 'Policy:\"%s\"->%s' % (policy.name, exc.message)
        raise exc


def checkPoliciesUnqiueness(policies):
    logger.debug("Check uniqueness of policies.")
    for policy in policies:
        for comp_policy in policies:
            if policy.name == comp_policy and policy != comp_policy:
                raise NotUniqueException("policy:\"%s\" is not unique." % policy.name)
        logger.debug("policy \"%s\" is unique." % policy.name)


def checkAlarm(alarm):
    try:
        # check that the meter is available
        if alarm.meter_name:
            if alarm.meter_name in METERS:
                logger.debug("meter_name \"%s\" is available." % alarm.meter_name)
            else:
                raise NotFoundException(
                    "meter_name:\"%s\" is not available. Available meter names:%s" % (alarm.meter_name, METERS))
        else:
            raise NotDefinedException("meter_name:\"%s\" is not defined.")
        # check that the statistic is available
        if alarm.statistic in STATISTICS:
            logger.debug("statistic \"%s\" is available." % alarm.statistic)
        else:
            raise NotFoundException(
                "statistic:\"%s\" is not available. Available statistics: %s" % (alarm.statistic, STATISTICS))
        # check that the evaluation period is an interger greater than 0
        if alarm.evaluation_periods:
            if isinstance(alarm.evaluation_periods, (long, int)):
                if alarm.evaluation_periods > 0:
                    logger.debug("evaluation_periods \"%s\" is valid." % alarm.evaluation_periods)
                else:
                    raise InvalidInputException(
                        "evaluation_periods:\"%s\" is not valid. It must be greater than 0." % alarm.evaluation_periods)
            else:
                raise TypeErrorException(
                    "evaluation_periods:\"%s\" is not valid. It must be an integer." % alarm.evaluation_periods)
        else:
            raise NotDefinedException("evaluation_periods is not defined.")
        if alarm.threshold:
            if isinstance(alarm.threshold, (long, int)):
                logger.debug("threshold \"%s\" is valid." % alarm.threshold)
            else:
                raise TypeErrorException("threshold:\"%s\" is not valid. It must be an integer." % alarm.threshold)
        else:
            raise NotDefinedException("threshold is not defined.")
        if alarm.comparison_operator:
            if alarm.comparison_operator in COMPARISON_OPERATORS:
                logger.debug("comparison_operator \"%s\" is available." % alarm.comparison_operator)
            else:
                NotFoundException("comparison_operator:\"%s\" is not available. Available comparison operators: %s" % (
                    alarm.comparison_operator, COMPARISON_OPERATORS))
        else:
            raise NotDefinedException("comparison_operator is not defined.")
    except Exception, exc:
        exc.message = 'Alarm->%s' % exc.message
        raise exc


def checkAction(action):
    try:
        # check adjustment type
        if action.adjustment_type:
            if action.adjustment_type in ADJUSTMENT_TYPES:
                logger.debug("adjustment_type \"%s\" is available." % action.adjustment_type)
            else:
                raise NotFoundException("adjustment_type:\"%s\" is not available. Available adjustment types: %s" % (
                    action.adjustment_type, ADJUSTMENT_TYPES))
        else:
            raise NotDefinedException("adjustment_type:\"%s\" is not defined.")
        # check scaling adjustment
        if action.scaling_adjustment:
            if isinstance(action.scaling_adjustment, (long, int)):
                logger.debug("scaling_adjusment \"%s\" is valid." % action.scaling_adjustment)
            else:
                raise TypeErrorException(
                    "scaling_adjusment:\"%s\" is not valid. It must be an integer." % action.scaling_adjustment)
        else:
            raise NotDefinedException("scaling_adjusment is not defined.")
        # check cooldown
        if action.cooldown:
            if isinstance(action.cooldown, (long, int)):
                if action.cooldown > 0:
                    logger.debug("cooldown \"%s\" is valid." % action.cooldown)
                else:
                    raise InvalidInputException("cooldown:\"%s\" must be greater than 0" % action.cooldown)
            else:
                raise TypeErrorException("cooldown:\"%s\" is not valid. It must be an integer." % action.cooldown)
        else:
            raise NotDefinedException("cooldown is not defined.")
    except Exception, exc:
        exc.message = 'Action->%s' % exc.message
        raise exc


def checkImage(image):
    db = DatabaseManager()
    existing_images = db.get_all(Image)
    if image.name in [existing_image.name for existing_image in existing_images]:
        logger.debug("image \"%s\" is available." % image)
    else:
        raise NotFoundException(
            "image:\"%s\" is not available. Available images: %s" % (
                image, [existing_image.name for existing_image in existing_images]))


def checkFlavor(flavor):
    db = DatabaseManager()
    existing_flavors = db.get_all(Flavor)
    if flavor.name in [existing_flavor.name for existing_flavor in existing_flavors]:
        logger.debug("flavor \"%s\" is available." % flavor)
    else:
        raise NotFoundException(
            "flavor:\"%s\" is not available. Available flavors: %s" % (
                flavor, [existing_flavor.name for existing_flavor in existing_flavors]))


def checkKey(key):
    db = DatabaseManager()
    existing_keys = db.get_all(Key)
    if key.name in [existing_key.name for existing_key in existing_keys]:
        logger.debug("key \"%s\" is available." % key)
    else:
        raise NotFoundException(
            "key:\"%s\" is not available. Available keys: %s" % (
                key, [existing_key.name for existing_key in existing_keys]))


def checkSize(size={}):
    if size.get('def'):
        if isinstance(size.get('def'), (long, int)):
            if size.get('def') >= 0:
                logger.debug("default size \"%s\" is valid." % size.get('def'))
            else:
                raise InvalidInputException("default size:\"%s\" must be bigger than 0." % size.get('def'))
        else:
            raise TypeErrorException("default size:\"%s\" must be an integer." % size.get('def'))
    else:
        raise NotDefinedException("default size is not defined.")
    if size.get('min'):
        if isinstance(size.get('min'), (long, int)):
            if size.get('min') >= 0:
                logger.debug("minimal size \"%s\" is valid." % size.get('min'))
            else:
                raise InvalidInputException(
                    "minimal size:\"%s\" is not valid. minimal_size must be bigger than 0." % size.get('min'))
        else:
            raise TypeErrorException("minimal size:\"%s\" must be an integer." % size.get('min'))
    else:
        raise NotDefinedException("minimal size is not defined.")
    if size.get('max'):
        if isinstance(size.get('max'), (long, int)):
            if size.get('max') >= 0:
                logger.debug("maximal size \"%s\" is valid." % size.get('max'))
            else:
                raise InvalidInputException(
                    "maximal size:\"%s\" is not valid. maximal size must be bigger than 0." % size.get('max'))
        else:
            raise TypeErrorException("maximal size:\"\%s\" must be an integer." % size.get('max'))
    else:
        raise NotDefinedException("maximal size is not defined.")
    if size.get('min') and size.get('max'):
        if size.get('min') <= size.get('max'):
            logger.debug(
                "minimal size \"%s\" and maximal size \"%s\" are valid. minimal size is equal or lower than maximal size." % (
                    size.get('min'), size.get('max')))
        else:
            raise InvalidInputException(
                "minimal size:\"%s\" and maximal size:\"%s\" are not valid. minimal size must be equal or lower than maximal size." % (
                    size.get('min'), size.get('max')))


def checkNetwork(network):
    try:
        db = DatabaseManager()
        existing_networks = db.get_all(Network)
        found_private_net = False
        found_subnet = False
        found_public_net = False
        for existing_network in existing_networks:
            if network.private_net == existing_network.ext_id and not found_private_net:
                if existing_network.public == False:
                    logger.debug("private_network \"%s\" is available." % network.private_net)
                    found_private_net = True
                else:
                    raise InvalidInputException(
                        "private_network:\"%s\" is available but it is marked as public and not as private as defined." % network.private_net)
                for subnet in existing_network.subnets:
                    if network.private_subnet == subnet.ext_id and not found_subnet:
                        found_subnet = True
                if found_subnet:
                    logger.debug("private_subnet \"%s\" is available." % network.private_subnet)
                else:
                    raise InvalidInputException("private_subnet:\"%s\" is not available." % network.private_subnet)
            if network.public_net == existing_network.ext_id and not found_public_net:
                if existing_network.public == True:
                    logger.debug("public_network \"%s\" is available." % network.public_net)
                    found_public_net = True
                else:
                    raise InvalidInputException(
                        "network:\"%s\" is available but it is marked as private and not as public as defined." % network.public_net)
        if not network.private_net and not network.private_subnet and not network.public_net:
            logger.debug("Networks were not defined.")
        elif network.private_net and network.private_subnet and network.public_net:
            if found_private_net and found_subnet and found_public_net:
                logger.debug("All defined networks are available for network: %s" % network)
            if not found_private_net:
                raise NotFoundException("Not found private network: %s" % network)
            if not found_subnet:
                raise NotFoundException("Not found private subnet network: %s" % network)
            if not found_public_net:
                raise NotFoundException("Not found public network: %s" % network)
        elif network.private_net and network.private_subnet and not network.public_net:
            if found_private_net and found_subnet and not found_public_net:
                logger.debug("All defined networks are available for network: %s" % network)
            if not found_private_net:
                raise NotFoundException("Not found private network: %s" % network)
            if not found_subnet:
                raise NotFoundException("Not found private subnet network: %s" % network)
        elif not network.private_net and network.public_net:
            raise InvalidInputException("Private net is not defined but the public.")
        else:
            raise InvalidInputException("Error while checking networks.")
    except Exception, exc:
        exc.message = 'Network:\"%s\"->%s' % (network.name, exc.message)
        raise exc


def checkNetworksUniqueness(networks):
    logger.debug("\"Check uniqueness of networks.\"")
    for network in networks:
        for comp_network in networks:
            if network.name == comp_network.name and network != comp_network:
                raise NotUniqueException("network:\"%s\" is not unique." % network.name)
        logger.debug("network \"%s\" is unique." % network.name)


def checkServiceType(service_type):
    db = DatabaseManager()
    services = db.get_all(Service)
    found = False
    for service in services:
        if service.service_type == service_type:
            found = True
            logger.debug("service_type \"%s\" is available." % service_type)
    if not found:
        raise NotFoundException(
            "service_type:\"%s\" is not available. Available service_types:%s" % (
                service_type, [service.service_type for
                               service in services]))


def checkSecurityGroup(security_group):
    try:
        logger.debug("Check security group \"%s\"." % security_group.name)
        for rule in security_group.rules:
            checkRule(rule)
    except Exception, exc:
        exc.message = 'SecurityGroup:\"%s\"->%s' % (security_group.name, exc.message)
        raise exc


def checkSecurityGroupUniqueness(security_group):
    db = DatabaseManager()
    existing_security_groups = db.get_all(SecurityGroup)
    logger.debug("Check uniqueness of name of the security group \"%s\"." % security_group.name)
    for existing_security_group in existing_security_groups:
        if security_group.name == existing_security_group.name and security_group != existing_security_group:
            raise NotUniqueException("SecurityGroup:\"%s\" is already existing." % security_group.name)
    logger.debug("Check rules of security group \"%s\"." % security_group.name)


def checkRule(rule):
    try:
        if rule.name:
            logger.debug("Check rule \"%s\"." % rule.name)
        else:
            raise NotDefinedException("name is not defined.")
        # check remote_ip_prefix
        if rule.remote_ip_prefix:
            a = re.compile(
                "^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)/([012345]?[1-9]|[6]?[0-4])$")
            if a.match(rule.remote_ip_prefix):
                logger.debug("remote_ip_prefix:\"%s\" for rule %s is valid." % (rule.remote_ip_prefix, rule.name))
            else:
                raise InvalidInputException("remote_ip_prefix:\"%s\"is not valid. Example: \"0.0.0.0/0\"." % (
                    rule.remote_ip_prefix))
        else:
            raise NotDefinedException("remote_ip_prefix is not defined.")
        # check protocol
        if rule.protocol:
            if rule.protocol in PROTOCOLS:
                logger.debug("protocol \"%s\" is available." % rule.protocol)
            else:
                raise NotFoundException(
                    "protocol:\"%s\" is not available. Available protocols are: %s." % (rule.protocol, PROTOCOLS))
        else:
            raise NotDefinedException("protocol is not defined.")
        # check defined ports
        port_min = 0
        port_max = 65535
        if rule.port_range_min and rule.port_range_max:
            if not isinstance(rule.port_range_min, (long, int)):
                try:
                    rule.port_range_min = int(rule.port_range_min)
                except Exception:
                    raise TypeErrorException(
                        "port_range_min:\"%s\" is not valid. It must be an integer." % rule.port_range_min)
            if not isinstance(rule.port_range_max, (long, int)):
                try:
                    rule.port_range_max = int(rule.port_range_max)
                except Exception:
                    raise TypeErrorException(
                        "port_range_max:\"%s\" is not valid. It must be an integer." % rule.port_range_max)
            if rule.port_range_min <= rule.port_range_max:
                logger.debug(
                    "port_range is valid (%s <= %s)." % (rule.port_range_min, rule.port_range_max))
            else:
                raise InvalidInputException(
                    "port_range is not valid (%s <= %s). port_range_min is bigger than port_range_max" % (
                        rule.port_range_min, rule.port_range_max))
            if rule.port_range_min >= port_min and rule.port_range_min <= port_max:
                logger.debug("port_range_min \"%s\" for rule %s is valid (%s >= %s and %s <= %s)." % (
                    rule.port_range_min, rule.name, rule.port_range_min, port_min, rule.port_range_min, port_max))
            else:
                raise InvalidInputException(
                    "port_range_min:\"%s\" is not valid (%s >= %s and %s <= %s). \"port_range_min\" is not in range." % (
                        rule.port_range_min, rule.port_range_min, port_min, rule.port_range_min, port_max))
            if rule.port_range_max >= port_min and rule.port_range_max <= port_max:
                logger.debug("port_range_max \"%s\" for rule %s is valid (%s >= %s and %s <= %s)." % (
                    rule.port_range_max, rule.name, rule.port_range_max, port_min, rule.port_range_max, port_max))
            else:
                raise InvalidInputException(
                    "port_range_max:\"%s\" is not valid (%s >= %s and %s <= %s). \"port_range_max\" is not in range." % (
                        rule.port_range_max, rule.port_range_max, port_min, rule.port_range_max, port_max))
        elif rule.port_range_min and not rule.port_range_max:
            raise InvalidInputException(
                "port range is not valid. Found \"port_range_min\":%s but no \"port_range_max\"." % (
                    rule.port_range_min))
        elif not rule.port_range_min and rule.port_range_max:
            raise InvalidInputException(
                "port_range is not valid. Found \"port_range_max\":%s but no \"port_range_min\"." % (
                    rule.port_range_max))
        else:
            logger.debug("port_range is not defined.")
    except Exception, exc:
        exc.message = 'Rule:\"%s\"->%s' % (rule.name, exc.message)
        raise exc


def checkRuleUnqiueness(rules=[]):
    logger.debug("Check uniqueness of security group rules.")
    for rule in rules:
        try:
            for comp_rule in rules:
                if rule.name == comp_rule.name and rule != comp_rule:
                    raise InvalidInputException("rule:\"%s\" is not unique." % rule.name)
            logger.debug("rule \"%s\" is unique." % rule.name)
        except Exception, exc:
            exc.message = 'Rule:\"%s\"->%s' % (rule.name, exc.message)
            raise exc


def checkService(service):
    try:
        # check flavor
        logger.debug("Check flavor of service \"%s\"." % service.service_type)
        if service.flavor:
            checkFlavor(service.flavor)
        else:
            raise NotDefinedException("flavor is not defined.")

        # check image
        logger.debug("Check image of service \"%s\"." % service.service_type)
        if service.image:
            checkImage(service.image)
        else:
            raise NotDefinedException("image is not defined.")

        # check keypair if provided
        logger.debug("Check key of service \"%s\"." % service.service_type)
        if service.key:
            checkKey(service.key)

        # check size
        logger.debug("Check size of service \"%s\"." % service.service_type)
        if service.size:
            checkSize(service.size)
        # check networks
        logger.debug("Check networks of service \"%s\"." % service.service_type)
        for network in service.networks:
            checkNetwork(network)

        # check requirements
        if service.requirements:
            logger.debug("Check requirements of service \"%s\"." % service.service_type)
            for requirement in service.requirements:
                checkRequirement(requirement)
    except Exception, exc:
        exc.message = 'Service:\"%s\"->%s' % (service.service_type, exc.message)
        raise exc


def checkServiceUniqueness(service):
    db = DatabaseManager()
    # check uniqueness of service
    logger.debug("Check uniqueness of name of the service %s." % service.service_type)
    if service.service_type:
        for existing_service in db.get_all(Service):
            if service.service_type == existing_service.service_type and service != existing_service:
                raise NotUniqueException(
                    "Service:\"%s\" is already existing." % service.service_type)
    else:
        raise NotDefinedException("service_type is not defined.")


def checkRequirement(requirement):
    try:
        if requirement.name:
            logger.debug("Check requirement with name \"%s\"" % requirement.name)
        else:
            raise NotDefinedException("name of requirement is not defined.")
        if requirement.parameter:
            if requirement.parameter in PARAMETERS:
                logger.debug("parameter \"%s\" is available" % requirement.parameter)
            else:
                raise NotFoundException(
                    "parameter:\"%s\" is not available. Available parameters:%s" % (requirement.parameter, PARAMETERS))
        else:
            raise NotDefinedException("parameter is not defined.")
        if requirement.source:
            logger.debug("source \"%s\" is defined." % requirement.source)
        else:
            raise NotDefinedException("source is not defined.")
        if requirement.obj_name:
            logger.debug("obj_name \"%s\" of requirement is defined." % requirement.obj_name)
        else:
            raise NotDefinedException("obj_name is not defined.")
    except Exception, exc:
        exc.message = 'Requirement:\"%s\"->%s' % (requirement.name, exc.message)
        raise exc


def checkRequirementsDependencies(requirements=[], service_instances=[]):
    for requirement in requirements:
        try:
            counter = 0
            logger.debug("Check dependencies for requirement \"%s\"." % requirement.name)
            for service_instance in service_instances:
                if requirement.source == service_instance.name:
                    logger.debug("source \"%s\" was found." % requirement.source)
                    if requirement.parameter == 'private_ip' or requirement.parameter == 'public_ip':
                        logger.debug("parameter \"%s\" is available." % requirement.parameter)
                        for obj in service_instance.networks:
                            if requirement.obj_name == obj.name:
                                logger.debug("obj_name \"%s\" was found." % requirement.obj_name)
                                counter += 1
                    else:
                        raise InvalidInputException("parameter:\"%s\" is not available." % requirement.parameter)
            if counter == 0:
                raise NotFoundException("requirement:\"%s\" was not found (\"source:%s\",  \"obj_name:%s\")." % (
                    requirement.name, requirement.source, requirement.obj_name))
            elif counter == 1:
                logger.debug("requirement \"%s\" is valid." % requirement.name)
            else:
                raise InvalidInputException("is not valid. Found sources or objects several times.")
        except Exception, exc:
            exc.message = 'Requirement:\"%s\"->%s' % (requirement.name, exc.message)
            raise exc


def checkRequirementsUniqueness(requirements=[]):
    logger.debug("Check uniqueness of requirement names.")
    for requirement in requirements:
        try:
            logger.debug("Check requirement uniqueness of name \"%s\"." % requirement.name)
            counter = 0
            for comp_requirement in requirements:
                if requirement.name == comp_requirement.name:
                    counter += 1
            if counter == 0:
                raise InvalidInputException("name:\"%s\" was not found." % requirement.name)
            elif counter == 1:
                logger.debug("name \"%s\" is unique." % requirement.name)
            elif counter > 1:
                raise InvalidInputException(
                    "name:\"%s\" is not valid. Found several requirements with the same name. Name must be unique." % requirement.name)
        except Exception, exc:
            exc.message = 'Requirement:\"%s\"->%s' % (requirement.name, exc.message)
            raise exc
