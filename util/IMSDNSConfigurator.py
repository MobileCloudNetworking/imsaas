__author__ = 'gca'

import os
import DNSaaSClient


class ImsDnsClient():

    def __init__(self):
        self.dns_api_ip = os.environ['DNSAAS_IP']
        self.dns_ip = os.environ['DNS_IP']
        DNSaaSClient.DNSaaSClientCore.apiurlDNSaaS='http://%s:8080' %self.dns_api_ip
        self.tokenID = os.environ['OS_AUTH_TOKEN']
        if 'test' in os.environ['TOPOLOGY']:
            return
        if 'standalone' in os.environ['TOPOLOGY']:
            # In case of a standalone topology we need to create also the domains
            DNSaaSClient.createDomain('epc.mnc001.mcc001.3gppnetwork.org','admin@mcn.pt',self.tokenID)
            DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='ns',record_type='A',record_data=self.dns_ip,tokenId=self.self.tokenID)
            DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='dns',record_type='A',record_data=self.dns_ip,tokenId=self.self.tokenID)
        DNSaaSClient.createRecord("epc.mnc001.mcc001.3gppnetwork.org", '', 'NAPTR', "10 50 \"s\" \"SIP+D2U\" \"\" _sip._udp", self.tokenID,priority = 10 )
        DNSaaSClient.createRecord("epc.mnc001.mcc001.3gppnetwork.org", '', 'NAPTR', "20 50 \"s\" \"SIP+D2U\" \"\" _sip._udp", self.tokenID,priority = 10 )

    def create_records_cscfs(self, cscfs_ip):
        self.__create_records_icscf(cscfs_ip)
        self.__create_records_pcscf(cscfs_ip)
        self.__create_records_scscf(cscfs_ip)

    def __create_records_pcscf(self, pcscf_ip):
        DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='pcscf',record_type='A',record_data=pcscf_ip,tokenId=self.tokenID)
        DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='pcscf-rx',record_type='A',record_data=pcscf_ip,tokenId=self.tokenID)
        DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='pcscf-rxrf',record_type='A',record_data=pcscf_ip,tokenId=self.tokenID)
        DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='pcscf-rf',record_type='A',record_data=pcscf_ip,tokenId=self.tokenID)
        DNSaaSClient.createRecord("epc.mnc001.mcc001.3gppnetwork.org", "_sip.pcscf", "SRV", "0 4060 pcscf.epc.mnc001.mcc001.3gppnetwork.org.", tokenId=self.tokenID, priority = 1)
        DNSaaSClient.createRecord("epc.mnc001.mcc001.3gppnetwork.org", "_sip._tcp.pcscf", "SRV", "0 4060 pcscf.epc.mnc001.mcc001.3gppnetwork.org.", tokenId=self.tokenID, priority = 1)

    def __create_records_icscf(self, icscf_ip):
        DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='icscf',record_type='A',record_data=icscf_ip,tokenId=self.tokenID)
        DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='icscf-cx',record_type='A',record_data=icscf_ip,tokenId=self.tokenID)
        DNSaaSClient.createRecord("epc.mnc001.mcc001.3gppnetwork.org", "_sip.icscf", "SRV", "0 5060 icscf.epc.mnc001.mcc001.3gppnetwork.org.", tokenId=self.tokenID, priority = 1)
        DNSaaSClient.createRecord("epc.mnc001.mcc001.3gppnetwork.org", "_sip._udp.icscf", "SRV", "0 5060 icscf.epc.mnc001.mcc001.3gppnetwork.org.", tokenId=self.tokenID, priority = 1)
        DNSaaSClient.createRecord("epc.mnc001.mcc001.3gppnetwork.org", "_sip._tcp.icscf", "SRV", "0 5060 icscf.epc.mnc001.mcc001.3gppnetwork.org.", tokenId=self.tokenID, priority = 1)
        DNSaaSClient.createRecord("epc.mnc001.mcc001.3gppnetwork.org", "_sip._udp.epc", "SRV", "0 5060 epc.mnc001.mcc001.3gppnetwork.org.", tokenId=self.tokenID, priority = 1)
        DNSaaSClient.createRecord("epc.mnc001.mcc001.3gppnetwork.org", "_sip._tcp", "SRV", "0 5060 epc.mnc001.mcc001.3gppnetwork.org.", tokenId=self.tokenID, priority = 1)
        DNSaaSClient.createRecord("epc.mnc001.mcc001.3gppnetwork.org", "_sip.epc", "SRV", "0 5060 epc.mnc001.mcc001.3gppnetwork.org.", tokenId=self.tokenID, priority = 1)
        # TODO change
        DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='',record_type='A',record_data=icscf_ip,tokenId=self.tokenID)


    def __create_records_scscf(self, scscf_ip):
        DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='scscf',record_type='A',record_data=scscf_ip,tokenId=self.tokenID)
        DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='scscf-cx',record_type='A',record_data=scscf_ip,tokenId=self.tokenID)
        DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='scscf-cxrf',record_type='A',record_data=scscf_ip,tokenId=self.tokenID)
        DNSaaSClient.createRecord("epc.mnc001.mcc001.3gppnetwork.org", "_sip.scscf", "SRV", "0 6060 scscf.epc.mnc001.mcc001.3gppnetwork.org.", tokenId=self.tokenID, priority = 1)
        DNSaaSClient.createRecord("epc.mnc001.mcc001.3gppnetwork.org", "_sip._tcp.scscf", "SRV", "0 6060 scscf.epc.mnc001.mcc001.3gppnetwork.org.", tokenId=self.tokenID, priority = 1)
        DNSaaSClient.createRecord("epc.mnc001.mcc001.3gppnetwork.org", "_sip._udp.scscf", "SRV", "0 6060 scscf.epc.mnc001.mcc001.3gppnetwork.org.", tokenId=self.tokenID, priority = 1)

    def create_records_hss_1(self, hss_1_ip):
        DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='hss-1',record_type='A',record_data=hss_1_ip,tokenId=self.tokenID)

    def create_records_hss_2(self, hss_2_ip):
        DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='hss-2',record_type='A',record_data=hss_2_ip,tokenId=self.tokenID)

    def create_records_slf(self, slf_ip):
        DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='slf',record_type='A',record_data=slf_ip,tokenId=self.tokenID)

    def create_records_test(self,test_ip):
        print "testing dns entry with ip %s"%test_ip

    def configure_dns_entry(self, service_type, hostanme):
        return {
            'hss': (self.create_records_hss_1 if "hss-1" in hostanme
                    else self.create_records_hss_2),
            'slf': self.create_records_slf,
            'cscfs': self.create_records_cscfs,
            'test': self.create_records_test,
        }[service_type]