import logging
from emm_exceptions.NotFoundException import NotFoundException
from novaclient import client
from util.SysUtil import SysUtil

__author__ = 'lto'

logger = logging.getLogger('EMMLogger')

class Client:

    def __init__(self):
        conf = SysUtil().get_sys_conf()
        self.nova = client.Client('2', conf['os_username'], conf['os_password'], conf['os_tenant'], conf['os_auth_url'])

    def list_servers(self):
        res = self.nova.servers.list()
        for s in res:
            logger.debug(s)
            for k, v in s.networks.iteritems():
                for ip in v:
                    try:
                        logger.debug(self.get_floating_ip(ip))
                    except:
                        continue

    def get_floating_ip(self, ip):
        res = self.nova.floating_ips.list()
        for _fip in res:
            if _fip.ip == ip:
                return _fip
        raise NotFoundException("Floating ip " + ip + " not found")

    def get_floating_ips(self):
        res = self.nova.floating_ips.list()
        return res

    def set_ips(self, unit):
        for k, v in self.nova.servers.get(unit.ext_id).networks.iteritems():
                for ip in v:
                    try:
                        unit.floating_ips[k] = self.get_floating_ip(ip).ip
                        logger.debug(ip + " is a floating ip")
                    except NotFoundException as e:
                        unit.ips[k] = ip
                        logger.debug(ip + " is a fixed ip")
        logger.debug("ips: " + str(unit.ips))
        logger.debug("floating_ips: " + str(unit.floating_ips))