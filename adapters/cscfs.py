__author__ = 'gca'


from interfaces.ServiceAdapter import ServiceAdapter as ABCServiceAdapter
import httplib, urllib, urllib2
import json

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

    def preinit(self, config):
        """
        sends the preinit method based on the received config parameters
        curl -X POST -H "Content-Type:application/json" -d "{\"parameters\":[\"mgmt=$ICSCF_MGMT_ADDR\",\"$ZABBIX_IP\"]}" http://$ICSCF_MGMT_ADDR:8390/icscf/preinit

        :return:
        """
        parameters = []
        for net_name, net_ip in config['ips'].items():
            parameters.append("%s=%s;"%(net_name,net_ip))
        parameters.append(config['zabbix_ip'])

        request = {"parameters":parameters}
        connection = httplib.HTTPConnection('%s:8390' % config['ips'].get('mgmt'))
        print "I'm the cscfs adapter, preinit cscfs service, parameters %s, request %s" %(parameters,str(json.dumps(request)))
        connection.request('POST', '/%s/preinit'%self.SCSCF_NAME, json.dumps(request), self.headers)
        response = connection.getresponse()
        resp = (response.read())
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
        connection = httplib.HTTPConnection('%s:8390' % config['ips'].get('mgmt'))
        print "I'm the cscfs adapter, install icscf service, parameters %s" %(parameters)
        connection.request('POST', '/%s/install'%self.ICSCF_NAME, json.dumps(request), self.headers)
        response = connection.getresponse()
        resp = (response.read())
        print "I'm the cscfs adapter, installing icscf service, received resp %s" %resp


        # scscf
        parameters = []
        parameters.append(config['ips'].get('mgmt'))
        parameters.append(self.SCSCF_DIAMETER_PORT)
        parameters.append(self.SCSCF_PORT)

        # create request scscf
        request = {"parameters":parameters}
        connection = httplib.HTTPConnection('%s:8390' % config['ips'].get('mgmt'))
        print "I'm the cscfs adapter, install scscf service, parameters %s" %(parameters)
        connection.request('POST', '/%s/install'%self.SCSCF_NAME, json.dumps(request), self.headers)
        response = connection.getresponse()
        resp = (response.read())
        print "I'm the cscfs adapter, installing scscf service, received resp %s" %resp


        # pcscf
        parameters = []
        parameters.append(config['ips'].get('mgmt'))
        parameters.append(self.PCSCF_PORT)

        # create request icscf
        request = {"parameters":parameters}
        connection = httplib.HTTPConnection('%s:8390' % config['ips'].get('mgmt'))
        print "I'm the cscfs adapter, install pcscf service, parameters %s" %(parameters)
        connection.request('POST', '/%s/install'%self.PCSCF_NAME, json.dumps(request), self.headers)
        response = connection.getresponse()
        resp = (response.read())
        print "I'm the cscfs adapter, installing pcscf service, received resp %s" %resp

        return True

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

    def terminate(self):
        """
        Terminate the service
        :return:
        """
        pass

if __name__ == '__main__':
    c = CscfsAdapter()
    config = {}
    config['hostname'] = "test"
    config['ips'] = {'mgmt':'160.85.4.46'}
    #config['ips'] = {'mgmt':'localhost'}
    config['zabbix_ip'] = '192.168.5.5'
    c.preinit(config)

    c.install(config)


