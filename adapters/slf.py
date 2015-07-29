__author__ = 'gca'

from interfaces.ServiceAdapter import ServiceAdapter as ABCServiceAdapter
import httplib
import json
import socket, time, datetime
import logging

logger = logging.getLogger(__name__)

class SlfAdapter(ABCServiceAdapter):
    def __init__(self):
        """
        Initializes a new ServiceAdapter.
        :return:
        """
        self.headers = {'Content-type': 'application/json'}

        self.HOST_NAME_BY_ORCH = ""
        self.PUB_IP = ""
        # 0 means we are not using a local database
        # ensure the database service is installed
        # and configured before starting this service
        self.LocalDB = "1"

        self.SLF_NAME = "slf"
        self.USE_SLF = "false"
        self.SLF_PORT = "13868"

        self.VAR_SLF_BIND = "localhost"
        self.VERSION = "5G"
        # -------------------------------------------------------#
        #	Parameters for dns relation
        # -------------------------------------------------------#
        self.DNS_REALM = "epc.mnc001.mcc001.3gppnetwork.org"
        self.DNS_LISTEN = ""
        self.DNS_IP = ""
        # -------------------------------------------------------#
        # Parameters for hss relation
        # -------------------------------------------------------#
        self.HSS_MGMT_ADDR = ""
        self.HSS_NAME = "hss"  # most likely the name given by orchestrator (e.g. hss-125683782)
        self.HSS_PORT = "3868"
        self.HSS_MGMT_ADDR = ""
        self.HSS_ENTRY = "%s.%s" % (self.HSS_NAME, self.DNS_REALM)
        # -------------------------------------------------------#
        # Parameters for cscfs relation
        # -------------------------------------------------------#
        self.SCSCF_NAME = "scscf"
        self.SCSCF_PORT = "6060"
        self.SCSCF_LISTEN = "0.0.0.0"
        self.ICSCF_NAME = "icscf"
        self.ICSCF_PORT = "5060"
        self.ICSCF_ENTRY = "icscf.%s" % self.DNS_REALM
        self.SCSCF_ENTRY = "scscf.%s" % self.DNS_REALM
        self.PCSCF_ENTRY = "pcscf.%s" % self.DNS_REALM
        # -------------------------------------------------------#
        #	Parameters for db relation
        # -------------------------------------------------------#
        self.DB_HOST = "localhost"
        self.DB_IP = ""

        self.DEFAULT_ROUTE = self.HSS_ENTRY
        self.SLF_ENTRY = "%s.%s" % (self.SLF_NAME, self.DNS_REALM)

    def preinit(self, config):
        """
        sends the preinit method based on the received config parameters
        curl -X POST -H "Content-Type:application/json" -d "{\"parameters\":[\"mgmt=$ICSCF_MGMT_ADDR\",\"$ZABBIX_IP\"]}" http://$ICSCF_MGMT_ADDR:8390/icscf/preinit

        :return:
        """

        while True:
            # Setup socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            now = datetime.datetime.now()
            now_text = now.strftime("%Y-%m-%d %H:%M:%S")
            try:
                # Issue the socket connect on the host:port
                sock.connect((config['floating_ips'].get('mgmt'), 8390))
            except Exception, e:
                logger.error("%s %d closed - Exception thrown when attempting to connect. " % (now_text, 8390))
            else:
                logger.debug("%s %d open" % (now_text, 8390))
                sock.close()
                break
            time.sleep(5)

        parameters = []
        for net_name, net_ip in config['ips'].items():
            parameters.append("%s=%s;" % (net_name, net_ip))
        parameters.append(config['zabbix_ip'])

        request = {"parameters": parameters}
        logger.info("preinit slf service, parameters %s, request %s" % (
            parameters, str(json.dumps(request))))
        resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "preinit", "slf")
        logger.info("preinit slf services, received resp %s" % resp)

        return True

    def install(self, config):
        """
        Creates a new Service based on the config file.
        :return:
        """
        self.VAR_HSS_ENTRY='%s.%s' % (config['hostname'], self.DNS_REALM)
        self.VAR_HSS_BIND = config['ips'].get('mgmt')
        # hss parameters
        parameters = []
        parameters.append(self.LocalDB)
        # create request hss
        request = {"parameters": parameters}
        logger.info("install slf service, parameters %s" % request)
        resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "install", "slf")
        print "I'm the slf adapter, installing slf service, received resp %s" % resp


    def add_dependency(self, config, ext_unit, ext_service):
        """
        Add the dependency between this service and the external one
        :return:
        """

        if "hss" in ext_service.service_type:
            # external dependency with the cscfs
            # curl -X POST -H "Content-Type:application/json" -d "{\"parameters\":[\"$HSS_NAME\",\"$DNS_REALM\",\"$HSS_PORT\"]}" http://$SLF_MGMT_ADDR:8390/dra/addRelation/hss
            parameters = []
            parameters.append(ext_unit.hostname)
            parameters.append(self.DNS_REALM)
            parameters.append("3868")
            request = {"parameters":parameters}
            resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "addRelation", "slf", "hss")
            logger.info("resolving dependency with hss service, received resp %s" %resp)
        if "dns" in ext_service.service_type:
            # external dependency with the cscfs
            # curl -X POST -H "Content-Type:application/json" -d "{\"parameters\":[\"$DNS_IP\",\"$DNS_REALM\",\"$DNS_LISTEN\"]}"
            # http://$HSS_MGMT_ADDR:8390/chess/addRelation/dns
            parameters = []
            parameters.append(ext_unit.ips.get('mgmt'))
            parameters.append(self.DNS_REALM)
            parameters.append(config['ips'].get('mgmt'))
            request = {"parameters":parameters}
            resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "addRelation", "slf", "dns")
            logger.info("resolving dependency with dns service, received resp %s" %resp)

    def remove_dependency(self, config, ext_service):
        """
        Remove the dependency between this service and the external one
        :return:
        """
        pass

    def pre_start(self, config):
        """
        Send the pre-start request

        :param config:
        :return:
        """

        pass

    def start(self, config):
        """
        Sending start requests to the different components
        curl -X POST -H "Content-Type:application/json" -d "{\"parameters\":[]}" http://$HSS_MGMT_ADDR:8390/chess/start

        :param config:
        :return:
        """

        # hss
        parameters = []
        # create request hss
        request = {"parameters": parameters}
        logger.info("install slf service, parameters %s" % parameters)
        resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "start", "slf")
        logger.info("installing slf service, received resp %s" % resp)


    def terminate(self):
        """
        Terminate the service
        :return:
        """
        pass



    def __send_request(self, ip, request, method, vnf, ext_vnf=None):
        """
        :return:
        """
        connection = httplib.HTTPConnection('%s:8390' % ip)
        if ext_vnf is None:
            connection.request('POST', '/%s/%s' % (vnf, method), json.dumps(request), self.headers)
        else:
            connection.request('POST', '/%s/%s/%s' % (vnf, method, ext_vnf), json.dumps(request), self.headers)
        response = connection.getresponse()
        return (response.read())


    def __split_ip(self, ip):
        """Split a IP address given as string into a 4-tuple of integers."""
        return tuple(int(part) for part in ip.split('.'))


if __name__ == '__main__':
    c = SlfAdapter()
    config = {}
    config['hostname'] = "test"
    config['ips'] = {'mgmt': '160.85.4.54'}
    config['floating_ips'] = {'mgmt': '160.85.4.54'}
    # config['ips'] = {'mgmt':'localhost'}
    config['zabbix_ip'] = '192.168.5.5'
    c.preinit(config)
    # c.install(config)
    # c.pre_start(config)
    c.start(config)


