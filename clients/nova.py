import logging

from novaclient import client

from emm_exceptions.NotFoundException import NotFoundException
from model.Entities import Key, Flavor, Image, Quotas


__author__ = 'lto'

logger = logging.getLogger('EMMLogger')


class Client:
    def __init__(self, conf=None):
        if not conf:
            from util.SysUtil import SysUtil

            self.conf = SysUtil().get_sys_conf()
        else:
            self.conf = conf
        self.nova = client.Client('2', self.conf['os_username'], self.conf['os_password'], self.conf['os_tenant'],
                                  self.conf['os_auth_url'])

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

    def get_images(self, object=True):
        images_repr = self.nova.images.list()
        images = []
        for image_repr in images_repr:
            if object:
                images.append(Image(name=image_repr.name, ext_id=image_repr.id, status=image_repr.status,
                                    created=image_repr.created, updated=image_repr.updated))
            else:
                images.append(image_repr._info)
        return images

    def get_flavors(self, object=True):
        flavors_repr = self.nova.flavors.list()
        flavors = []
        for flavor_repr in flavors_repr:
            if object:
                flavors.append(Flavor(name=flavor_repr.name, ram=flavor_repr.ram, vcpus=flavor_repr.vcpus))
            else:
                flavors.append(flavor_repr._info)
        return flavors

    def get_keys(self, object=True):
        keys_repr = self.nova.keypairs.list()
        keys = []
        for key_repr in keys_repr:
            if object:
                keys.append(Key(name=(key_repr.name)))
            else:
                keys.append(key_repr._info)
        return keys

    def get_quotas(self, object=True):
        quotas_repr = self.nova.quotas.get(tenant_id=self.conf.get('os_tenant'))
        if object:
            quotas = (Quotas(**quotas_repr._info))
        else:
            quotas = (quotas_repr._info)
        return quotas