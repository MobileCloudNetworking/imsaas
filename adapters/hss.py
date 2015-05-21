__author__ = 'gca'

from interfaces.ServiceAdapter import ServiceAdapter as ABCServiceAdapter
import httplib
import json
import socket, time, datetime


class HssAdapter(ABCServiceAdapter):
    def __init__(self):
        """
        Initializes a new ServiceAdapter.
        :return:
        """
        self.headers = {'Content-type': 'application/json'}
        self.icscf_diameter_port = "3869"
        self.SCSCF_NAME = "scscf"
        self.SCSCF_DIAMETER_PORT = "3870"
        self.SCSCF_PORT = "6060"
        self.SCSCF_LISTEN = "0.0.0.0"
        self.ICSCF_NAME = "icscf"
        self.ICSCF_DIAMETER_PORT = "3869"
        self.ICSCF_PORT = "5060"
        self.PCSCF_NAME = "pcscf"
        self.PCSCF_PORT = "4060"
        self.HSS_MGMT_ADDR = ""
        self.HOST_NAME_BY_ORCH = ""
        self.PUB_IP = ""
        # 0 means we are not using a local database
        # ensure the database service is installed
        # and configured before starting this service
        self.LocalDB = "1"

        self.VAR_CONSOLE_PORT_ONE = "10003"
        self.VAR_CONSOLE_PORT_TWO = "10000"
        self.VAR_CONSOLE_PORT_BIND_ONE = "0.0.0.0"
        self.VAR_CONSOLE_PORT_BIND_TWO = "0.0.0.0"
        self.VAR_HSS_DNS_REALM = "openepc.test"  # mainly used for dra/slf relation
        self.VAR_HSS_ENTRY ="hss.%s" % self.VAR_HSS_DNS_REALM  # mainly used for dra/slf relation
        self.VAR_HSS_PORT = "3868"
        self.VAR_HSS_BIND = "localhost"
        self.VERSION = "5G"
        # -------------------------------------------------------#
        # Parameters for hss relation
        # -------------------------------------------------------#
        self.HSS_MGMT_ADDR = ""
        self.HSS_NAME = "hss"  # most likely the name given by orchestrator (e.g. hss-125683782)
        self.HSS_PORT = "3868"
        # -------------------------------------------------------#
        #	Parameters for slf relation
        #--------------------------------------------------------#
        self.SLF_NAME = "slf"
        self.USE_SLF = "true"
        self.SLF_PORT = "13868"

        # -------------------------------------------------------#
        #	Parameters for dns relation
        # -------------------------------------------------------#
        self.DNS_REALM = "openepc.test"
        self.DNS_REA_SLASHED = "openepc\\\.test"
        self.ICSCF_ENTRY = "icscf.%s" % self.DNS_REALM
        self.SCSCF_ENTRY = "scscf.%s" % self.DNS_REALM
        self.PCSCF_ENTRY = "pcscf.%s" % self.DNS_REALM
        self.HSS_ENTRY = "%s.%s" % (self.HSS_NAME, self.DNS_REALM)
        self.SLF_ENTRY = "%s.%s" % (self.SLF_NAME, self.DNS_REALM)

        # -------------------------------------------------------#
        #	Parameters for db relation
        # -------------------------------------------------------#
        self.DB_HOST = "localhost"

        self.DEFAULT_ROUTE = self.HSS_ENTRY

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
                print "%s %d closed - Exception thrown when attempting to connect. " % (now_text, 8390)
            else:
                print  "%s %d open" % (now_text, 8390)
                sock.close()
                break
            time.sleep(5)

        parameters = []
        for net_name, net_ip in config['ips'].items():
            parameters.append("%s=%s;" % (net_name, net_ip))
        parameters.append(config['zabbix_ip'])

        request = {"parameters": parameters}
        print "I'm the hss adapter, preinit hss service, parameters %s, request %s" % (
            parameters, str(json.dumps(request)))
        resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "preinit", "chess")
        print "I'm the hss adapter, preinit hss services, received resp %s" % resp

        return True

    def install(self, config):
        """
        Creates a new Service based on the config file.
        curl -X POST -H "Content-Type:application/json" -d "{\"parameters\":[\"$LocalDB\",\"$HOST_NAME_BY_ORCH\",\"$PUB_IP\",\"$VAR_CONSOLE_PORT_ONE\",
        \"$VAR_CONSOLE_PORT_TWO\",\"$VAR_CONSOLE_PORT_BIND_ONE\",\"$VAR_CONSOLE_PORT_BIND_TWO\",\"$VAR_HSS_ENTRY\",
        \"$VAR_HSS_PORT\",\"$VAR_HSS_BIND\",\"$VERSION\"]}" http://$HSS_MGMT_ADDR:8390/chess/install
        :return:
        """

        self.VAR_HSS_ENTRY='%s.%s' % (config['hostname'], self.DNS_REALM)
        self.VAR_HSS_BIND = config['ips'].get('mgmt')

        # hss parameters
        parameters = []
        parameters.append(self.LocalDB)
        parameters.append(config['hostname'])
        parameters.append(config['floating_ips'].get('mgmt'))
        parameters.append(self.VAR_CONSOLE_PORT_ONE)
        parameters.append(self.VAR_CONSOLE_PORT_TWO)
        parameters.append(self.VAR_CONSOLE_PORT_BIND_ONE)
        parameters.append(self.VAR_CONSOLE_PORT_BIND_TWO)
        parameters.append(self.VAR_HSS_ENTRY)
        parameters.append(self.VAR_HSS_PORT)
        parameters.append(self.VAR_HSS_BIND)
        parameters.append(self.VERSION)

        # create request hss
        request = {"parameters": parameters}
        print "I'm the hss adapter, install hss service, parameters %s" % (request)
        resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "install", "chess")
        print "I'm the hss adapter, installing hss service, received resp %s" % resp


    def add_dependency(self, config, ext_unit, ext_service):
        """
        Add the dependency between this service and the external one
        :return:
        """
        print "hss adapter ext_service.service_type %s" %ext_service.service_type

        if "cscfs" in ext_service.service_type:
        # external dependency with the cscfs
        # curl -X POST -H "Content-Type:application/json" -d "{\"parameters\":[]}" http://$HSS_MGMT_ADDR:8390/chess/addRelation/icscf
            parameters = []
            request = {"parameters":parameters}
            resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "addRelation", "chess", "icscf")
            print "I'm the cscfs adapter, resolving dependency with hss service, received resp %s" %resp
        if "dra" in ext_service.service_type:
        # external dependency with the cscfs
        # curl -X POST -H "Content-Type:application/json" -d "{\"parameters\":[]}" http://$HSS_MGMT_ADDR:8390/chess/addRelation/icscf
            parameters = []
            request = {"parameters":parameters}
            resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "addRelation", "chess", "icscf")
            print "I'm the cscfs adapter, resolving dependency with hss service, received resp %s" %resp


    def remove_dependency(self, config, ext_service):
        """
        Remove the dependency between this service and the external one
        :return:
        """
        pass

    def pre_start(self, config):
        """
        Send the pre-start request

        curl -X POST -H "Content-Type:application/json" -d "{\"parameters\":[\"$VAR_CONSOLE_PORT_ONE\",
        \"$VAR_CONSOLE_PORT_TWO\",\"$VAR_CONSOLE_PORT_BIND_ONE\",\"$VAR_CONSOLE_PORT_BIND_TWO\",
        \"$DNS_REALM\",\"$VAR_HSS_ENTRY\",\"$SLF_ENTRY\",\"$USE_SLF\",\"$SLF_PORT\",\"$ICSCF_PORT\",
        \"$SCSCF_PORT\",\"$VAR_HSS_PORT\",\"$VAR_HSS_BIND\",\"$DB_HOST\",\"$DEFAULT_ROUTE\"]}"
         http://$HSS_MGMT_ADDR:8390/chess/preStart
        :param config:
        :return:
        """

        # hss

        self.VAR_HSS_ENTRY='%s.%s' % (config['hostname'], self.DNS_REALM)
        self.VAR_HSS_BIND = config['ips'].get('mgmt')

        # hss parameters
        parameters = []
        parameters.append(self.VAR_CONSOLE_PORT_ONE)
        parameters.append(self.VAR_CONSOLE_PORT_TWO)
        parameters.append(self.VAR_CONSOLE_PORT_BIND_ONE)
        parameters.append(self.VAR_CONSOLE_PORT_BIND_TWO)
        parameters.append(self.DNS_REALM)
        parameters.append(self.VAR_HSS_ENTRY)
        parameters.append(self.SLF_ENTRY)
        parameters.append(self.USE_SLF)
        parameters.append(self.SLF_PORT)
        parameters.append(self.ICSCF_PORT)
        parameters.append(self.SCSCF_PORT)
        parameters.append(self.VAR_HSS_PORT)
        parameters.append(self.VAR_HSS_BIND)
        parameters.append(self.DB_HOST)
        parameters.append(self.DEFAULT_ROUTE)



        # create request hss
        request = {"parameters": parameters}
        print "I'm the hss adapter, pre-starting hss service, parameters %s" % (request)
        resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "preStart", "chess")
        print "I'm the hss adapter, pre-starting hss service, received resp %s" % resp


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
        print "I'm the hss adapter, install hss service, parameters %s" % (parameters)
        resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "start", "chess")
        print "I'm the hss adapter, installing hss service, received resp %s" % resp


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
    c = HssAdapter()
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


