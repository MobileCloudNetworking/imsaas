__author__ = 'gca'

from interfaces.ServiceAdapter import ServiceAdapter as ABCServiceAdapter
import httplib
import json
import socket, time, datetime

import logging

logger = logging.getLogger(__name__)

class DBAdapter(ABCServiceAdapter):
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


        # -------------------------------------------------------#
        # Parameters for hss relation
        # -------------------------------------------------------#
        self.HSS_MGMT_ADDR = ""
        self.HSS_DB_NAME="hss_db_chess"
        self.HSS_DB_USER="hss"
        self.HSS_DB_PW="heslo"
        self.HSS_DB_PROVI="1" # if set to 0 provision access is NOT granted
        # -------------------------------------------------------#
        # Parameters for slf relation
        # -------------------------------------------------------#
        self.SLF_MGMT_ADDR = ""
        self.SLF_DB_NAME="dra_db"
        self.SLF_DB_USER="dra"
        self.SLF_DB_PW="dra"
        self.SLF_DB_PROVI="1"	# if set to 0 provision access is NOT granted


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
        logger.info("preinit db service, parameters %s, request %s" % (
            parameters, str(json.dumps(request))))
        resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "preinit", "mysql")
        logger.info("preinit db services, received resp %s" % resp)

        return True

    def install(self, config):
        """
        Creates a new Service based on the config file.
        :return:
        """

        # hss parameters
        parameters = []
        # create request hss
        request = {"parameters": parameters}
        logger.info("install mysql service, sending request %s to ip %s" % (request,config['floating_ips'].get('mgmt')))
        resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "install", "mysql")
        logger.info("installing mysql service, received resp %s" % resp)


    def add_dependency(self, config, ext_unit, ext_service):
        """
        Add the dependency between this service and the external one
        :return:
        """
        print "slf adapter ext_service.service_type %s" %ext_service.service_type

        if "hss" in ext_service.service_type:
            # external dependency with the cscfs
            # curl -X POST -H "Content-Type:application/json" -d "{\"parameters\":[\"$HSS_NAME\",\"$DNS_REALM\",\"$HSS_PORT\"]}" http://$SLF_MGMT_ADDR:8390/dra/addRelation/hss
            parameters = []
            parameters.append(self.HSS_DB_NAME)
            parameters.append(self.HSS_DB_USER)
            parameters.append(self.HSS_DB_PW)
            parameters.append(ext_unit.ips.get('mgmt'))
            parameters.append(self.HSS_DB_PROVI)

            request = {"parameters":parameters}
            resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "addRelation", "mysql", "db")
            logger.info("resolving dependency with hss service, received resp %s" %resp)

        if "slf" in ext_service.service_type:
            # external dependency with the cscfs
            # curl -X POST -H "Content-Type:application/json" -d "{\"parameters\":[\"$HSS_NAME\",\"$DNS_REALM\",\"$HSS_PORT\"]}" http://$SLF_MGMT_ADDR:8390/dra/addRelation/hss
            parameters = []
            parameters.append(self.SLF_DB_NAME)
            parameters.append(self.SLF_DB_USER)
            parameters.append(self.SLF_DB_PW)
            parameters.append(ext_unit.ips.get('mgmt'))
            parameters.append(self.SLF_DB_PROVI)
            request = {"parameters":parameters}
            resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "addRelation", "mysql", "db")
            logger.info("resolving dependency with slf service, received resp %s" %resp)

    def remove_dependency(self, config, ext_unit, ext_service):
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
        logger.info("start mysql service, parameters %s" % parameters)
        resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "start", "mysql")
        logger.info("starting mysql service, received resp %s" % resp)

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
    c = DBAdapter()
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


