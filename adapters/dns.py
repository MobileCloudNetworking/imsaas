__author__ = 'gca'

from interfaces.ServiceAdapter import ServiceAdapter as ABCServiceAdapter
import httplib
import json
import socket, time, datetime, logging
from util import add_dns_pcscf, add_dns_slf, add_dns_scscf, add_dns_chess, add_dns_icscf

logger = logging.getLogger(__name__)


class DNSAdapter(ABCServiceAdapter):
    def __init__(self):
        """
        Initializes a new ServiceAdapter.
        :return:
        """
        self.headers = {'Content-type': 'application/json'}

        # -------------------------------------------------------#
        #	Parameters for dns
        # -------------------------------------------------------#
        self.DNS_MGMT_ADDR=""
        self.ZABBIX_IP=""

        self.nameserver="ns.openepc.test."
        self.realm="openepc.test."
        self.additional="dns.openepc.test."



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
                logger.error("%s %d open" % (now_text, 8390))
                sock.close()
                break
            time.sleep(5)

        parameters = []
        for net_name, net_ip in config['ips'].items():
            parameters.append("%s=%s;" % (net_name, net_ip))
        parameters.append(config['zabbix_ip'])

        request = {"parameters": parameters}
        logger.info("DNS adapter, preinit hss service, parameters %s, request %s" % (parameters, str(json.dumps(request))))
        resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "preinit", "moniker")
        logger.info("I'm the hss adapter, preinit hss services, received resp %s" % resp)

    def install(self, config):
        """
        Creates a new Service based on the config file.
        :return:
        """
        parameters = []

        # add basic nameserver ( is in general done by java adapters... Thus now by hand)
        # curl -X POST -H "Content-Type:application/json" -d "{\"parameters\":[]}"
        #  http://$DNS_MGMT_ADDR:8390/moniker/start
        request = {"parameters": parameters}
        logger.info("DNS adapter, starting moniker service, parameters %s" % request)
        resp = self.__send_request(config['floating_ips'].get('mgmt'), request, "start", "moniker")
        logger.info("DNS adapter, started moniker service, received resp %s" % resp)

        # add basic nameserver ( is in general done by java adapters... Thus now by hand)
        # curl -X POST -H "Content-Type: application/json" -d "{\"name\" : \"$nameserver\" }"
        # http://$DNS_MGMT_ADDR:9001/v1/servers
        request = {"name": self.nameserver}
        logger.info("DNS adapter, sending request to add basic nameserver to moniker with parameters %s" % request)
        resp = self.__send_request_to_moniker(config['floating_ips'].get('mgmt'), request, "servers")
        logger.info("DNS adapter request sent to moniker for adding basic nameserver, received resp %s" % resp)

        # add basic realm ( is in general done by java adapters... Thus now by hand)
        # remember the id of the created realm!!
        # curl -X POST -H "Content-Type:application/json" -d "{\"name\" : \"$realm\" ,\"ttl\" : 3600 ,
        # \"email\" : \"opensdncore@fokus.fraunhofer.de\"}"
        #  http://$DNS_MGMT_ADDR:9001/v1/domains
        # sleep 4s
        request = {"name": self.realm, "ttl": 3600, "email": "opensdncore@fokus.fraunhofer.de"}
        logger.info("DNS adapter, adding basic realm, parameters %s" % request)
        resp = self.__send_request_to_moniker(config['floating_ips'].get('mgmt'), request, "domains")
        logger.info("DNS adapter, added basic realm, received resp %s" % resp)

        time.sleep(4)

        domain_id = json.loads(resp)['id']
        logger.debug("parsed domain server %s" %domain_id)

        # ENTRY=$(echo {\"name\" : \"$nameserver\",\"type\" : \"A\" ,\"data\" : \"$OWN_IP\"})
        # curl -X POST -H "Content-Type:application/json" -d "$ENTRY" http://$DNS_MGMT_ADDR:9001/v1/domains/$ID/records
        request = {"name": self.nameserver, "type": "A", "data": config['floating_ips'].get('mgmt')}
        logger.info("creating bsic record %s " %request)
        resp = self.__send_request_to_moniker(config['floating_ips'].get('mgmt'), request, "domains", domain_id)
        logger.info("created basic record %s " %resp)

        # ENTRY=$(echo {\"name\" : \"$additional\",\"type\" : \"A\" ,\"data\" : \"$OWN_IP\"})
        # curl -X POST -H "Content-Type:application/json" -d "$ENTRY" http://$DNS_MGMT_ADDR:9001/v1/domains/$ID/records
        request = {"name": self.additional, "type": "A", "data": config['floating_ips'].get('mgmt')}
        logger.info("creating bsic record %s " %request)
        resp = self.__send_request_to_moniker(config['floating_ips'].get('mgmt'), request, "domains", domain_id)
        logger.info("created basic record %s " %resp)

    def add_dependency(self, config, ext_unit, ext_service):
        """
        Add the dependency between this service and the external one
        :return:
        """

        if "cscfs" in ext_service.service_type:
            # add relation with all cscfs services
            logger.info("adding dns records for cscfs components")
            add_dns_pcscf.create_records(ext_unit.ips.get('mgmt'), config['floating_ips'].get('mgmt'), self.realm)
            add_dns_icscf.create_records(ext_unit.ips.get('mgmt'), config['floating_ips'].get('mgmt'), self.realm)
            add_dns_scscf.create_records(ext_unit.ips.get('mgmt'), config['floating_ips'].get('mgmt'), self.realm)
        if "hss" in ext_service.service_type:
            # add relation with all cscfs services
            logger.info("adding dns records hss components")
            add_dns_chess.create_records(ext_unit.ips.get('mgmt'), config['floating_ips'].get('mgmt'), self.realm, ext_unit.hostname)
        if "slf" in ext_service.service_type:
            # add relation with all cscfs services
            logger.info("adding dns records for slf components")
            add_dns_slf.create_records(ext_unit.ips.get('mgmt'), config['floating_ips'].get('mgmt'), self.realm)
        if "dra" in ext_service.service_type:
            # add relation with all cscfs services
            logger.info("adding dns records for slf components")
            add_dns_slf.create_records(ext_unit.ips.get('mgmt'), config['floating_ips'].get('mgmt'), self.realm)



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

        pass

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

    def __send_request_to_moniker(self, ip, request, type, internal_id=None):
        """
        :return:
        """
        connection = httplib.HTTPConnection('%s:9001' % ip)
        if internal_id is None:
            connection.request('POST', '/v1/%s' % type, json.dumps(request), self.headers)
        else:
            connection.request('POST', '/v1/%s/%s/records' % (type, internal_id,), json.dumps(request), self.headers)
        response = connection.getresponse()
        return (response.read())


    def __split_ip(self, ip):
        """Split a IP address given as string into a 4-tuple of integers."""
        return tuple(int(part) for part in ip.split('.'))


if __name__ == '__main__':
    c = DNSAdapter()
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


