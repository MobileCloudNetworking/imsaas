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
        self.SCSCF_NAME="scscf"
        self.SCSCF_DIAMETER_PORT="3870"
        self.SCSCF_PORT="6060"
        self.SCSCF_LISTEN="0.0.0.0"
        self.ICSCF_NAME="icscf"
        self.ICSCF_DIAMETER_PORT="3869"
        self.ICSCF_PORT="5060"
        self.PCSCF_NAME="pcscf"
        self.PCSCF_PORT="4060"
        # -------------------------------------------------------#
        #	Parameters for hss relation
        # -------------------------------------------------------#
        self.HSS_MGMT_ADDR=""
        self.HSS_NAME="hss" 	# most likely the name given by orchestrator (e.g. hss-125683782)
        self.HSS_PORT="3868"
        # -------------------------------------------------------#
        #	Parameters for slf relation
        #-------------------------------------------------------#
        self.SLF_NAME="slf"
        self.USE_SLF="false"
        self.SLF_PORT="13868"

        # -------------------------------------------------------#
        #	Parameters for dns relation
        # -------------------------------------------------------#
        self.DNS_REALM="openepc.test"
        self.DNS_REA_SLASHED="openepc\\\.test"
        self.ICSCF_ENTRY="icscf.%s" % self.DNS_REALM
        self.SCSCF_ENTRY="scscf.%s" % self.DNS_REALM
        self.PCSCF_ENTRY="pcscf.%s" % self.DNS_REALM
        self.HSS_ENTRY="%s.%s" % (self.HSS_NAME,self.DNS_REALM)
        self.SLF_ENTRY="slf.%s" % self.DNS_REALM


        self.DEFAULT_ROUTE=self.HSS_ENTRY

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
                sock.connect((config['floating_ips'].get('mgmt'),8390))
            except Exception,e:
                print "%s %d closed - Exception thrown when attempting to connect. " % (now_text, 8390)
            else:
                print  "%s %d open" % (now_text, 8390)
                sock.close()
                break
            time.sleep(5)


        parameters = []
        for net_name, net_ip in config['ips'].items():
            parameters.append("%s=%s;"%(net_name,net_ip))
        parameters.append(config['zabbix_ip'])

        request = {"parameters":parameters}
        print "I'm the cscfs adapter, preinit cscfs service, parameters %s, request %s" %(parameters,str(json.dumps(request)))
        resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "preinit", "hss")
        print "I'm the cscfs adapter, preinit cscfs services, received resp %s" %resp

        return True

    def install(self, config):
        """
        Creates a new Service based on the config file.
        :return:
        """

        # icscf
        parameters = []
        parameters.append(config['ips'].get('mgmt'))
        parameters.append(self.ICSCF_DIAMETER_PORT)
        parameters.append(self.ICSCF_PORT)

        # create request icscf
        request = {"parameters":parameters}
        print "I'm the cscfs adapter, install icscf service, parameters %s" %(request)
        resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "install", "icscf")
        print "I'm the cscfs adapter, installing icscf service, received resp %s" %resp


    def add_dependency(self, config, ext_service):
        """
        Add the dependency between this service and the external one
        :return:
        """

        # external dependency with the database

        print "I'm the dummy adapter, installing dummy service, received config %s" %config

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

        # icscf
        parameters = []
        parameters.append(config['ips'].get('mgmt'))
        parameters.append(self.ICSCF_DIAMETER_PORT)
        parameters.append(self.ICSCF_PORT)
        parameters.append(self.DNS_REALM)
        parameters.append(self.DNS_REA_SLASHED)
        parameters.append(self.ICSCF_ENTRY)
        parameters.append(self.HSS_ENTRY)
        parameters.append(self.SLF_ENTRY)
        parameters.append(self.SLF_PORT)
        parameters.append(self.SCSCF_PORT)
        parameters.append(self.DEFAULT_ROUTE)
        parameters.append(self.USE_SLF)
        parameters.append(self.HSS_PORT)




        # create request icscf
        request = {"parameters":parameters}
        print "I'm the cscfs adapter, install icscf service, parameters %s" %(request)
        resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "preStart", "icscf")
        print "I'm the cscfs adapter, installing icscf service, received resp %s" %resp



    def start(self, config):
        """
        Sending start requests to the different components
        :param config:
        :return:
        """

        # icscf
        parameters = []
        # create request icscf
        request = {"parameters":parameters}
        print "I'm the cscfs adapter, install icscf service, parameters %s" %(parameters)
        resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "start", "icscf")
        print "I'm the cscfs adapter, installing pcscf service, received resp %s" %resp


    def terminate(self):
        """
        Terminate the service
        :return:
        """
        pass


    def __send_request(self, ip, request, method, vnf):
        """

        :return:
        """
        connection = httplib.HTTPConnection('%s:8390' % ip)
        connection.request('POST', '/%s/%s' % (vnf, method), json.dumps(request), self.headers)
        response = connection.getresponse()
        return (response.read())

    def __split_ip(self, ip):
        """Split a IP address given as string into a 4-tuple of integers."""
        return tuple(int(part) for part in ip.split('.'))


if __name__ == '__main__':
    c = HssAdapter()
    config = {}
    config['hostname'] = "test"
    config['ips'] = {'mgmt':'160.85.4.54'}
    config['floating_ips'] = {'mgmt':'160.85.4.54'}
    #config['ips'] = {'mgmt':'localhost'}
    config['zabbix_ip'] = '192.168.5.5'
    c.preinit(config)
    # c.install(config)
    # c.pre_start(config)
    c.start(config)


