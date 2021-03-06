__author__ = 'sruffino'

import json
import os
import requests

from interfaces.ServiceAdapter import ServiceAdapter as ABCServiceAdapter


class PgwuSgwuAdapter(ABCServiceAdapter):

    def __init__(self):
        """
        Initializes a new ServiceAdapter.
        :return:
        """
        # -------------------------------------------------------#
        #   Parameters for preinit/install
        # -------------------------------------------------------#
        self.PGWU_SGWU_ID="3812090105" # (e.g.: 3812090105 ) The unit id generated by orchestrator (or whatever ID generated by you )
        self.OFP_DATAPATH_ID="3812090105000000" # (e.g.: $PGWU_SGWU_ID000000) unit id with appended zeros to match length for datapath_id
        self.UPLOAD_FLOATING_NETWORK_CIDR="" # (e.g.: 192.168.95.0/24 ) Example from the wall
        self.PGWU_SGWU_NET_A_IP="4.4.4.10"
        self.PGWU_SGWU_NET_B_IP=""
        self.PGWU_SGWU_NET_MGMT_IP="3.3.3.10"
        self.PGWU_SGWU_NET_D_IP="5.5.5.10"
        self.ZABBIX_IP="9.9.9.9"
        self.PGW_U_Upload_Interface_IP=self.PGWU_SGWU_NET_B_IP
        self.PGW_U_Download_Interface_IP=self.PGWU_SGWU_NET_A_IP
        # -------------------------------------------------------#
        #   Paramters for gw relation
        # -------------------------------------------------------#
        self.GW_NET_A_IP="4.4.4.3"
        self.PGWU_NET_A_IP_ENDING_NUMBER="10" # The last number from the net_a IP of the pgwu-sgwu
        self.GW_NET_A_IP_ENDING_NUMBER="3" # The last number from the net_a IP of the gw
        self.VIRT_NET_A_IP="192.168.77." + self.PGWU_NET_A_IP_ENDING_NUMBER # e.g. 192.168.77.210 when pgwu-sgwu got 172.30.5.210
        self.VIRT_NET_A_GW_IP="192.168.77" + self.GW_NET_A_IP_ENDING_NUMBER # e.g. 192.168.77.204 when gw got 172.20.5.204
        # -------------------------------------------------------#
        #   Paramters for pgw_c relation
        # -------------------------------------------------------#
        self.PGW_C_Openflow_Transport_Protocol="tcp"
        self.PGW_C_Openflow_IP="3.3.3.30" # The MGMT_IP of pgw_c
        self.PGW_C_OpenFlow_Port="6634"
        # -------------------------------------------------------#


    def preinit(self, config):
        """
        sends the preinit method based on the received config parameters
        curl -X POST -H "Content-Type:application/json" -d \
        "{\"parameters\":[\"net_d=$PGWU_SGWU_NET_D_IP,mgmt=$PGWU_SGWU_NET_MGMT_IP,\
        net_a=$PGWU_SGWU_NET_A_IP\",\
        \"$ZABBIX_IP\"]}" http://$NAT_PUBLIC_IP:8390/pgw_u-sgw_u-5G/preinit
        :param config:
        :return:
        """

        parameters = []
        networks = ""
        for net_name, net_ip in config['ips'].items():
            networks = networks + ("%s=%s;"%(net_name,net_ip))
        parameters.append(networks)
        parameters.append(config['zabbix_ip'])

        request = {"parameters":parameters}
        print "I'm the pgwu-sgwu adapter, preinit pgwu-sgwu service, \
               parameters %s, request %s" %(parameters,str(json.dumps(request)))

        url = 'http://' + config['floating_ips'].get('mgmt') + \
              ':8390/pgw_u-sgw_u-5G/preinit'
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(request), headers=headers)

        print response.content
        print "I'm the pgwu-sgwu adapter, preinit pgwu-sgwu services, \
               received resp %s" %response

        return True

    def install(self, config):
        """
        Creates a new Service based on the config file.
        curl -X POST -H "Content-Type:application/json" -d \
        "{\"parameters\":[\"PGW-U-$PGWU_SGWU_ID\",\"$PGWU_SGWU_NET_MGMT_IP\",\
        \"$PGW_U_Upload_Interface_IP\",\"$PGW_U_Download_Interface_IP\",\
        \"$OFP_DATAPATH_ID\",\"true\",\"$UPLOAD_FLOATING_NETWORK_CIDR\"]}" \
        http://127.0.0.1:8390/pgw_u-sgw_u-5G/install
        :params config:
        :return:
        """

        exp_params = ['PGWU_SGWU_ID', 'PGWU_SGWU_NET_MGMT_IP', 'PGW_U_Upload_Interface_IP', 
                     'PGW_U_Download_Interface_IP', 'OFP_DATAPATH_ID',
                     'UPLOAD_FLOATING_NETWORK_CIDR']

        # pgwu-sgwu
        for v in exp_params:
            if v not in config:
                print "PGWU-SGWU adapter - install _ missing parameter: " + v
                return False

        parameters = []
        parameters.append('PGW-U-' + config['PGWU_SGWU_ID'])
        parameters.append(config['PGWU_SGWU_NET_MGMT_IP'])
        parameters.append(config['PGW_U_Upload_Interface_IP'])
        parameters.append(config['PGW_U_Download_Interface_IP'])
        parameters.append(config['OFP_DATAPATH_ID'])
        parameters.append(config['UPLOAD_FLOATING_NETWORK_CIDR'])

        # create request nat
        request = {"parameters":parameters}
        print "I'm the pgwu-sgwu adapter, install pgwu-sgwu service, parameters %s" %(parameters)
        
        url = 'http://' + config['floating_ips'].get('mgmt') + \
              ':8390/pgw_u-sgw_u-5G/install'
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(request), headers=headers)
        
        print response.content
        print "I'm the pgwu-sgwu adapter, installing pgwu-sgwu service, received resp %s" %response

        return True

    def pre_start(self, config):
        """
        Pre-start method
        curl -X POST -H "Content-Type:application/json" -d \
        "{\"parameters\":[\"PGW-U-$PGWU_SGWU_ID\",\"$PGWU_SGWU_NET_MGMT_IP\",\
        \"$PGW_U_Upload_Interface_IP\",\"$PGW_U_Download_Interface_IP\",\
        \"$OFP_DATAPATH_ID\",\"$PGW_C_Openflow_IP\",\"$PGW_C_OpenFlow_Port\"]}" \
        http://127.0.0.1:8390/pgw_u-sgw_u-5G/preStart
        :param config:
        :return:
        """

        exp_params = ['PGWU_SGWU_ID', 'PGWU_SGWU_NET_MGMT_IP', 'PGW_U_Upload_Interface_IP', 
                     'PGW_U_Download_Interface_IP', 'OFP_DATAPATH_ID', 'PGW_C_Openflow_IP',
                     'PGW_C_OpenFlow_Port']

        # pgwu-sgwu
        for v in exp_params:
            if v not in config:
                print "PGWU-SGWU adapter - preStart _ missing parameter: " + v
                return False

        parameters = []
        parameters.append('PGW-U-' + config['PGWU_SGWU_ID'])
        parameters.append(config['PGWU_SGWU_NET_MGMT_IP'])
        parameters.append(config['PGW_U_Upload_Interface_IP'])
        parameters.append(config['PGW_U_Download_Interface_IP'])
        parameters.append(config['OFP_DATAPATH_ID'])
        parameters.append(config['PGW_C_Openflow_IP'])
        parameters.append(config['PGW_C_OpenFlow_Port'])

        # create request nat
        request = {"parameters":parameters}
        print "I'm the pgwu-sgwu adapter, preStart pgwu-sgwu service, parameters %s" %(parameters)
        
        url = 'http://' + config['floating_ips'].get('mgmt') + \
              ':8390/pgw_u-sgw_u-5G/preStart'
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(request), headers=headers)
        
        print response.content
        print "I'm the pgwu-sgwu adapter, preStarting pgwu-sgwu service, received resp %s" %response

        return True

    def add_dependency(self, config, ext_service):
        """
        Add the dependency between this service and the external one
        curl -X POST -H "Content-Type:application/json" -d \
        "{\"parameters\":[\"$PGWU_SGWU_NET_A_IP\",\"$GW_NET_A_IP\", \
        \"$VIRT_NET_A_IP\",\"$VIRT_NET_A_GW_IP\"]}" \
        http://127.0.0.1:8390/pgw_u-sgw_u-5G/addRelation/gw

        curl -X POST -H "Content-Type:application/json" -d \
        "{\"parameters\":[\"$PGW_C_Openflow_Transport_Protocol\",\
        \"$PGW_C_Openflow_IP\",\"$PGW_C_OpenFlow_Port\"]}" \
        http://127.0.0.1:8390/pgw_u-sgw_u-5G/addRelation/pgw_c

        :return:
        """

        exp_params_gw = ['PGWU_SGWU_NET_A_IP', 'GW_NET_A_IP', 'VIRT_NET_A_IP', 
                     'VIRT_NET_A_GW_IP']

        exp_params_pgw_c = ['PGW_C_Openflow_Transport_Protocol', 'PGW_C_Openflow_IP', 
                            'PGW_C_OpenFlow_Port']

        parameters = []
        if ext_service == 'gw':

            for v in exp_params_gw:
                if v not in config:
                    print "PGWU-SGWU adapter - add_relation _ missing parameter: " + v
                    return False

            # parameters require a specific order
            parameters.append(config['PGWU_SGWU_NET_A_IP'])
            parameters.append(config['GW_NET_A_IP'])
            parameters.append(config['VIRT_NET_A_IP'])
            parameters.append(config['VIRT_NET_A_GW_IP'])
        elif ext_service == 'pgw_c':

            for v in exp_params_pgw_c:
                if v not in config:
                    print "PGWU-SGWU adapter - add_relation _ missing parameter: " + v
                    return False

            # parameters require a specific order
            parameters.append(config['PGW_C_Openflow_Transport_Protocol'])
            parameters.append(config['PGW_C_Openflow_IP'])
            parameters.append(config['PGW_C_OpenFlow_Port'])
        else:
            print ("PGWU-SGWU adapter - wrong ext_service")

       
        request = {"parameters":parameters}
        print "I'm the pgwu-sgwu adapter, adding " + ext_service +  " relation to pgwu-sgwu service, parameters %s" %(parameters)
        
        url = 'http://' + config['floating_ips'].get('mgmt')+ \
              ':8390/pgw_u-sgw_u-5G/addRelation/' + ext_service
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(request), headers=headers)
        
        print response.content
        print "I'm the pgwu-sgwu adapter, adding " + ext_service +  " relation to pgwu-sgwu service, received resp %s" %response
        return True


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
        print "I'm the pgwu-sgwu adapter, adding pgwu relation to pgwu-sgwu service, parameters %s" %(parameters)
        
        url = 'http://' + config['floating_ips'].get('mgmt') + ':8390/pgw_u-sgw_u-5G/start'
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(request), headers=headers)
        
        print response.content
        print "I'm the pgwu-sgwu adapter, adding pgwu relation to pgwu-sgwu service, received resp %s" %response
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
    
    c = PgwuSgwuAdapter()
	# since we use the proxy, no floating_ip needed
    pgw_floating_ip = '192.168.85.95'

    # preinit
    config = {}
    config['hostname'] = "pgwu-sgwu-1"
    config['ips'] = {'mgmt':'192.168.85.95', 'net_a':'172.19.5.95', 'net_d':'172.19.8.95'}
    config['zabbix_ip'] = '9.9.9.9'
    config['floating_ips'] = {'mgmt':pgw_floating_ip}
    c.preinit(config)
    
    # install
    config = {}
    config = {'OFP_DATAPATH_ID': '3812090105000000',
 'PGWU_SGWU_ID': '3812090105',
 'PGWU_SGWU_NET_MGMT_IP': '192.168.85.95',
 'PGW_U_Download_Interface_IP': '172.19.5.95',   #net_a
 'PGW_U_Upload_Interface_IP': '172.19.8.95',    # net_d
 'UPLOAD_FLOATING_NETWORK_CIDR': '130.92.70.128/25'}  #floating ip subnet cidr
    config['floating_ips'] = {'mgmt':pgw_floating_ip}
    c.install(config)

    # add dependency to gw(nat)
    config = {}
    config = {
    'PGWU_SGWU_NET_A_IP': '172.19.5.95',
    'GW_NET_A_IP':'172.19.5.96',
    'PGWU_NET_A_IP_ENDING_NUMBER':'95', # The last number from the net_a IP of the pgwu-sgwu
    'GW_NET_A_IP_ENDING_NUMBER':'96' # The last number from the net_a IP of the gw
    }
    config['VIRT_NET_A_IP'] = '192.168.77.' + config['PGWU_NET_A_IP_ENDING_NUMBER'] # e.g. 192.168.77.210 when pgwu-sgwu got 172.30.5.210
    config['VIRT_NET_A_GW_IP'] = '192.168.77.' + config['GW_NET_A_IP_ENDING_NUMBER'] # e.g. 192.168.77.204 when gw got 172.20.5.204
    config['floating_ips'] = {'mgmt':pgw_floating_ip}
    c.add_dependency(config, 'gw')

    # add dependency to pgw_c
    config = {}
    config = {
    'PGW_C_Openflow_Transport_Protocol':'tcp',
    'PGW_C_Openflow_IP':'192.168.85.97', # The MGMT_IP of mme
    'PGW_C_OpenFlow_Port':'6634'
    }
    config['floating_ips'] = {'mgmt':pgw_floating_ip}
    c.add_dependency(config, 'pgw_c')

    # prestart
    config = {}
    config = {
 'PGWU_SGWU_ID': '3812090105',
 'PGWU_SGWU_NET_MGMT_IP': '192.168.85.95',
 'PGW_U_Download_Interface_IP': '172.19.5.95',   #net_a
 'PGW_U_Upload_Interface_IP': '172.19.8.95',    # net_d
 'OFP_DATAPATH_ID': '3812090105000000',
 'PGW_C_Openflow_IP':'192.168.85.97', # The MGMT_IP of mme
 'PGW_C_OpenFlow_Port':'6634'
    }
    config['floating_ips'] = {'mgmt':pgw_floating_ip}
    c.pre_start(config)

    config = {}
    config['floating_ips'] = {'mgmt':pgw_floating_ip}
    c.start(config)

