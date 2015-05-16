__author__ = 'gca'


from interfaces.ServiceAdapter import ServiceAdapter as ABCServiceAdapter
import httplib
import json
import socket, time, datetime


class CscfsAdapter(ABCServiceAdapter):

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
        resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "preinit", "icscf")
        print "I'm the cscfs adapter, preinit cscfs services, received resp %s" %resp

        return True

    def install(self, config):
        """
        Creates a new Service based on the config file.
        curl -X POST -H "Content-Type:application/json" -d "{\"parameters\":[\"$ICSCF_MGMT_ADDR\",\"$ICSCF_DIAMETER_PORT\",\"$ICSCF_PORT\"]}" http://$ICSCF_MGMT_ADDR:8390/icscf/install
        curl -X POST -H "Content-Type:application/json" -d "{\"parameters\":[\"$SCSCF_MGMT_ADDR\",\"$SCSCF_DIAMETER_PORT\",\"$SCSCF_PORT\"]}" http://$SCSCF_MGMT_ADDR:8390/scscf/install
        curl -X POST -H "Content-Type:application/json" -d "{\"parameters\":[\"$PCSCF_MGMT_ADDR\",\"$PCSCF_PORT\"]}" http://$PCSCF_MGMT_ADDR:8390/pcscf/install
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


        # scscf
        parameters = []
        parameters.append(config['ips'].get('mgmt'))
        parameters.append(self.SCSCF_DIAMETER_PORT)
        parameters.append(self.SCSCF_PORT)

        # create request scscf
        request = {"parameters":parameters}
        print "I'm the cscfs adapter, install scscf service, parameters %s" %(parameters)
        resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "install", "scscf")
        print "I'm the cscfs adapter, installing scscf service, received resp %s" %resp


        # pcscf
        parameters = []
        parameters.append(config['ips'].get('mgmt'))
        parameters.append(self.PCSCF_PORT)

        # create request icscf
        request = {"parameters":parameters}
        print "I'm the cscfs adapter, install pcscf service, parameters %s" %(parameters)
        resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "install", "pcscf")
        print "I'm the cscfs adapter, installing pcscf service, received resp %s" %resp

        return True

    def add_dependency(self, config, ext_unit, ext_service):
        """
        Add the dependency between this service and the external one
        :return:
        """
        print "cscfs adapter ext_service.service_type %s" %ext_service.service_type

        if "hss" in ext_service.service_type:
        # external dependency with the hss
        # curl -X POST -H "Content-Type:application/json" -d "{\"parameters\":[\"$HSS_MGMT_ADDR\"]}" http://$ICSCF_MGMT_ADDR:8390/icscf/addRelation/chess
            print "resolving dependency with the hss with following information: %s, %s"%(ext_unit, ext_service)
            parameters = []
            parameters.append(ext_unit.ips.get('mgmt'))
            request = {"parameters":parameters}
            resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "addRelation", "icscf", "hss")
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
        curl -X POST -H "Content-Type:application/json" -d "{\"parameters\":[\"$ICSCF_LISTEN\",\"$ICSCF_DIAMETER_PORT\",
            \"$ICSCF_PORT\",\"$DNS_REALM\",\"$DNS_REA_SLASHED\",\"$ICSCF_ENTRY\",\"$HSS_ENTRY\",\"$SLF_ENTRY\",
            \"$SLF_PORT\",\"$SCSCF_PORT\",\"$DEFAULT_ROUTE\",\"$USE_SLF\",\"$HSS_PORT\"]}" http://$ICSCF_MGMT_ADDR:8390/icscf/preStart
        curl -X POST -H "Content-Type:application/json" -d "{\"parameters\":[\"$SCSCF_LISTEN\",\"$SCSCF_DIAMETER_PORT\",
            \"$SCSCF_PORT\",\"$DNS_REALM\",\"$DNS_REA_SLASHED\",\"$SCSCF_ENTRY\",\"$HSS_ENTRY\",\"$SLF_ENTRY\",\"$SLF_PORT\",
            \"$ICSCF_ENTRY\",\"$DEFAULT_ROUTE\",\"$USE_SLF\",\"$HSS_PORT\"]}" http://$SCSCF_MGMT_ADDR:8390/scscf/preStart
        curl -X POST -H "Content-Type:application/json" -d "{\"parameters\":[\"$PCSCF_LISTEN\",\"$PCSCF_PORT\",
            \"$DNS_REALM\",\"$DNS_REA_SLASHED\",\"$PCSCF_ENTRY\"]}" http://$PCSCF_MGMT_ADDR:8390/pcscf/preStart

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


        # scscf
        parameters = []
        parameters.append(config['ips'].get('mgmt'))
        parameters.append(self.SCSCF_DIAMETER_PORT)
        parameters.append(self.SCSCF_PORT)
        parameters.append(self.DNS_REALM)
        parameters.append(self.DNS_REA_SLASHED)
        parameters.append(self.SCSCF_ENTRY)
        parameters.append(self.HSS_ENTRY)
        parameters.append(self.SLF_ENTRY)
        parameters.append(self.SLF_PORT)
        parameters.append(self.SCSCF_PORT)
        parameters.append(self.DEFAULT_ROUTE)
        parameters.append(self.USE_SLF)
        parameters.append(self.HSS_PORT)

        # create request scscf
        request = {"parameters":parameters}
        print "I'm the cscfs adapter, install scscf service, parameters %s" %(parameters)
        resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "preStart", "scscf")
        print "I'm the cscfs adapter, installing scscf service, received resp %s" %resp


        # pcscf
        parameters = []
        parameters.append(config['ips'].get('mgmt'))
        parameters.append(self.PCSCF_PORT)
        parameters.append(self.DNS_REALM)
        parameters.append(self.DNS_REA_SLASHED)
        parameters.append(self.PCSCF_ENTRY)


        # create request pcscf
        request = {"parameters":parameters}
        print "I'm the cscfs adapter, install pcscf service, parameters %s" %(parameters)
        resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "preStart", "pcscf")
        print "I'm the cscfs adapter, installing pcscf service, received resp %s" %resp

        return True

    def start(self, config):
        """
        Sending start requests to the different components
        curl -X POST -H "Content-Type:application/json" -d "{\"parameters\":[]}" http://$ICSCF_MGMT_ADDR:8390/icscf/start
        curl -X POST -H "Content-Type:application/json" -d "{\"parameters\":[]}" http://$SCSCF_MGMT_ADDR:8390/scscf/start
        curl -X POST -H "Content-Type:application/json" -d "{\"parameters\":[]}" http://$PCSCF_MGMT_ADDR:8390/pcscf/start
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


        # scscf
        parameters = []
        # create request scscf
        request = {"parameters":parameters}
        print "I'm the cscfs adapter, install scscf service, parameters %s" %(parameters)
        resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "start", "scscf")
        print "I'm the cscfs adapter, installing scscf service, received resp %s" %resp

        # pcscf
        parameters = []
        # create request pcscf
        request = {"parameters":parameters}
        print "I'm the cscfs adapter, install pcscf service, parameters %s" %(parameters)
        resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "start", "pcscf")
        print "I'm the cscfs adapter, installing pcscf service, received resp %s" %resp


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
    c = CscfsAdapter()
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


