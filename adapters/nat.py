__author__ = 'sruffino'

import json
import os
import requests

from interfaces.ServiceAdapter import ServiceAdapter as ABCServiceAdapter


class NatAdapter(ABCServiceAdapter):

    def __init__(self):
        """
        Initializes a new ServiceAdapter.
        :return:
        """
        # -------------------------------------------------------#
        #	Parameters for preinit/install
        # -------------------------------------------------------#
        self.GW_NET_A_IP="4.4.4.3"
        self.GW_NET_MGMT_IP="3.3.3.3"
        self.ZABBIX_IP="160.85.4.61"
        # -------------------------------------------------------#
        #	Paramters for pgw_u relation
        # -------------------------------------------------------#
        self.STATIC_NUMBER="1" # defines which IP block to use (1->192.168.3.0/26 , 2->192.168.3.64/26 , 3->192.168.3.128/26 , 4->192.168.3.192/26)
        self.PGW_U_NET_A_IP="4.4.4.10"
        self.VIRT_NET_A_GW_IP=""
        self.VIRT_NET_A_PGWU_IP=""
        self.PGWU_NET_A_IP_ENDING_NUMBER="10" # The last number from the net_a IP of the pgwu-sgwu
        self.GW_NET_A_IP_ENDING_NUMBER="3" # The last number from the net_a IP of the gw
        self.CLOUD_MGMT_GW_IP="3.3.3.1" # e.g.: 172.67.0.1 for the wall testbed , the network address of mgmt network !
        self.VIRT_NET_A_PGWU_IP="192.168.77." + self.PGWU_NET_A_IP_ENDING_NUMBER # e.g. 192.168.77.210 when pgwu-sgwu got 172.30.5.210
        self.VIRT_NET_A_GW_IP="192.168.77." + self.GW_NET_A_IP_ENDING_NUMBER # e.g. 192.168.77.204 when gw got 172.20.5.204
        self.VIRT_NET_A_INTF="gwtun" + self.PGWU_NET_A_IP_ENDING_NUMBER # e.g. gwtun210 when pgwu-sgwu got 172.30.5.210


    def preinit(self, config):
        """
        sends the preinit method based on the received config parameters
        curl -X POST -H "Content-Type:application/json" \
        -d "{\"parameters\":[\"mgmt=$GW_NET_MGMT_IP,net_a=$GW_NET_A_IP\",\"$ZABBIX_IP\"]}" \
        http://$NAT_PUBLIC_IP:8390/gw/preinit

        :return:
        """

        parameters = []
        networks = ""
        for net_name, net_ip in config['ips'].items():
            networks = networks + ("%s=%s;"%(net_name,net_ip))
        parameters.append(networks)
        parameters.append(config['zabbix_ip'])

        request = {"parameters":parameters}
        print "I'm the nat adapter, preinit nat service, parameters %s, request %s" %(parameters,str(json.dumps(request)))

        #response = self.__send_request(config['floating_ips'].get('mgmt'), request, "preinit", "icscf")

        # payload = {'parameters':
        #            ['mgmt=' + self.GW_NET_MGMT_IP + ';net_a=' + self.GW_NET_A_IP + ';',
        #             self.ZABBIX_IP]}

        url = 'http://' + config['floating_ips'].get('mgmt') + ':8390/gw/preinit'
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(request), headers=headers)

        print response.content
        print "I'm the nat adapter, preinit nat services, received resp %s" %response

        return True

    def install(self, config):
        """
        Creates a new Service based on the config file.
        curl -X POST -H "Content-Type:application/json" \
        -d "{\"parameters\":[\"true\",\"5G\"]}" http://$NAT_PUBLIC_IP:8390/gw/install
         :return:
        """

        # nat
        parameters = []
        parameters.append("true")
        parameters.append("5G")

        # create request nat
        request = {"parameters":parameters}
        print "I'm the nat adapter, install nat service, parameters %s" %(parameters)
        
        url = 'http://' + config['floating_ips'].get('mgmt') + ':8390/gw/install'
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(request), headers=headers)
        
        print response.content
        print "I'm the nat adapter, installing nat service, received resp %s" %response

        return True

    def add_relation(self, config):
        """
        Add a relation with the PGWU.
        curl -X POST -H "Content-Type:application/json" \
        -d "{\"parameters\":[\"$GW_NET_A_IP\",\"$PGW_U_NET_A_IP\", \
        \"$GW_NET_MGMT_IP\",\"$CLOUD_MGMT_GW_IP\",\"$VIRT_NET_A_INTF\", \
        \"$VIRT_NET_A_GW_IP\",\"$VIRT_NET_A_PGWU_IP\",\"$STATIC_NUMBER\"]}" \
        http://$NAT_PUBLIC_IP:8390/gw/addRelation/pgwu
        """

        parameters = []

        for v in vars(self):
            if v not in config:
                print "NAT adapter - add_relation _ missing parameter: " + v
                return False

        # parameters require a specific order
        parameters.append(config['GW_NET_A_IP'])
        parameters.append(config['PGW_U_NET_A_IP'])
        parameters.append(config['GW_NET_MGMT_IP'])
        parameters.append(config['CLOUD_MGMT_GW_IP'])
        parameters.append(config['VIRT_NET_A_INTF'])
        parameters.append(config['VIRT_NET_A_GW_IP'])
        parameters.append(config['VIRT_NET_A_PGWU_IP'])
        parameters.append(config['STATIC_NUMBER'])
        
        request = {"parameters":parameters}
        print "I'm the nat adapter, adding pgwu relation to nat service, parameters %s" %(parameters)
        
        url = 'http://' + config['floating_ips'].get('mgmt') + ':8390/gw/addRelation/pgwu'
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(request), headers=headers)
        
        print response.content
        print "I'm the nat adapter, adding pgwu relation to nat service, received resp %s" %response
        return True

    def pre_start(self, config):
        """
        Pre-start method
        :param config:
        :return:
        """
        pass

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

    def start(self, config):
        """
        Sending start requests to the different components
        curl -X POST -H "Content-Type:application/json" \
        -d "{\"parameters\":[]}" http://$NAT_PUBLIC_IP:8390/gw/start        
        :return:
        """

        parameters = []

        request = {"parameters":parameters}
        print "I'm the nat adapter, adding pgwu relation to nat service, parameters %s" %(parameters)
        
        url = 'http://' + config['floating_ips'].get('mgmt') + ':8390/gw/start'
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(request), headers=headers)
        
        print response.content
        print "I'm the nat adapter, adding pgwu relation to nat service, received resp %s" %response
        return True

    def terminate(self):
        """
        Terminate the service
        :return:
        """
        pass

if __name__ == '__main__':
    # set http_proxy to epc-proxy VM
    os.environ['http_proxy']='http://130.92.70.187:3128'
    c = NatAdapter()
    nat_floating_ip = '192.168.85.96'  # since we use the proxy, no floating_ip needed

    config = {}
    config['hostname'] = "nat"
    config['ips'] = {'mgmt': '192.168.85.96', 'net_a': '172.19.5.96'}
    config['zabbix_ip'] = '30.30.30.30'
    config['floating_ips'] = {'mgmt': nat_floating_ip}
    c.preinit(config)

    config = {}
    config['floating_ips'] = {'mgmt': nat_floating_ip}
    c.install(config)

    config = {}
    config = {'CLOUD_MGMT_GW_IP': '192.168.85.1',
              'GW_NET_A_IP': '172.19.5.96',
              'GW_NET_A_IP_ENDING_NUMBER': '96',
              'GW_NET_MGMT_IP': '192.168.85.96',
              'PGWU_NET_A_IP_ENDING_NUMBER': '95',
              'PGW_U_NET_A_IP': '172.19.5.95',
              'STATIC_NUMBER': '1',
              'ZABBIX_IP': '9.9.9.9'}
    config['VIRT_NET_A_GW_IP'] = '192.168.77.' + config['GW_NET_A_IP_ENDING_NUMBER']
    config['VIRT_NET_A_INTF'] = 'gwtun' + config['PGWU_NET_A_IP_ENDING_NUMBER']
    config['VIRT_NET_A_PGWU_IP'] = '192.168.77.' + config['PGWU_NET_A_IP_ENDING_NUMBER']
    config['floating_ips'] = {'mgmt': nat_floating_ip}
    c.add_relation(config)

    config = {}
    config['floating_ips'] = {'mgmt': nat_floating_ip}
    c.start(config)

