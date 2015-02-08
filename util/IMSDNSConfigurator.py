__author__ = 'gca'



import os
import DNSaaSClient


class IMSDNSConfigurator:
    def __init__(self, dns_ip):
        self.dns_ip = dns_ip
        DNSaaSClient.DNSaaSClientCore.apiurlDNSaaS='http://%s:8080' %dns_ip
        tokenID = os.environ['OS_AUTH_TOKEN']
        DNSaaSClient.createRecord("epc.mnc001.mcc001.3gppnetwork.org", '', 'NAPTR', "10 50 \"s\" \"SIP+D2U\" \"\" _sip._udp", tokenID,priority = 10 )
        DNSaaSClient.createRecord("epc.mnc001.mcc001.3gppnetwork.org", '', 'NAPTR', "20 50 \"s\" \"SIP+D2U\" \"\" _sip._udp", tokenID,priority = 10 )

    def create_records_pcscf(pcscf_ip):
        DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='pcscf',record_type='A',record_data=pcscf_ip,tokenId=tokenID)
        DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='pcscf-rx',record_type='A',record_data=pcscf_ip,tokenId=tokenID)
        DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='pcscf-rxrf',record_type='A',record_data=pcscf_ip,tokenId=tokenID)
        DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='pcscf-rf',record_type='A',record_data=pcscf_ip,tokenId=tokenID)
        DNSaaSClient.createRecord("epc.mnc001.mcc001.3gppnetwork.org", "_sip.pcscf", "SRV", "0 4060 pcscf.epc.mnc001.mcc001.3gppnetwork.org.", tokenId=tokenID, priority = 1)
        DNSaaSClient.createRecord("epc.mnc001.mcc001.3gppnetwork.org", "_sip._tcp.pcscf", "SRV", "0 4060 pcscf.epc.mnc001.mcc001.3gppnetwork.org.", tokenId=tokenID, priority = 1)
        DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='epc',record_type='A',record_data=pcscf_ip,tokenId=tokenID)

    def create_records_icscf(icscf_ip):
        DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='icscf',record_type='A',record_data=icscf_ip,tokenId=tokenID)
        DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='icscf-cx',record_type='A',record_data=icscf_ip,tokenId=tokenID)
        DNSaaSClient.createRecord("epc.mnc001.mcc001.3gppnetwork.org", "_sip.icscf", "SRV", "0 5060 icscf.epc.mnc001.mcc001.3gppnetwork.org.", tokenId=tokenID, priority = 1)
        DNSaaSClient.createRecord("epc.mnc001.mcc001.3gppnetwork.org", "_sip._udp.icscf", "SRV", "0 5060 icscf.epc.mnc001.mcc001.3gppnetwork.org.", tokenId=tokenID, priority = 1)
        DNSaaSClient.createRecord("epc.mnc001.mcc001.3gppnetwork.org", "_sip._tcp.icscf", "SRV", "0 5060 icscf.epc.mnc001.mcc001.3gppnetwork.org.", tokenId=tokenID, priority = 1)
        DNSaaSClient.createRecord("epc.mnc001.mcc001.3gppnetwork.org", "_sip._udp.epc", "SRV", "0 5060 epc.mnc001.mcc001.3gppnetwork.org.", tokenId=tokenID, priority = 1)
        DNSaaSClient.createRecord("epc.mnc001.mcc001.3gppnetwork.org", "_sip._tcp", "SRV", "0 5060 epc.mnc001.mcc001.3gppnetwork.org.", tokenId=tokenID, priority = 1)
        DNSaaSClient.createRecord("epc.mnc001.mcc001.3gppnetwork.org", "_sip.epc", "SRV", "0 5060 epc.mnc001.mcc001.3gppnetwork.org.", tokenId=tokenID, priority = 1)


    def create_records_scscf(scscf_ip):
        DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='scscf',record_type='A',record_data=scscf_ip,tokenId=tokenID)
        DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='scscf-cx',record_type='A',record_data=scscf_ip,tokenId=tokenID)
        DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='scscf-cxrf',record_type='A',record_data=scscf_ip,tokenId=tokenID)
        DNSaaSClient.createRecord("epc.mnc001.mcc001.3gppnetwork.org", "_sip.scscf", "SRV", "0 6060 scscf.epc.mnc001.mcc001.3gppnetwork.org.", tokenId=tokenID, priority = 1)
        DNSaaSClient.createRecord("epc.mnc001.mcc001.3gppnetwork.org", "_sip._tcp.scscf", "SRV", "0 6060 scscf.epc.mnc001.mcc001.3gppnetwork.org.", tokenId=tokenID, priority = 1)
        DNSaaSClient.createRecord("epc.mnc001.mcc001.3gppnetwork.org", "_sip._udp.scscf", "SRV", "0 6060 scscf.epc.mnc001.mcc001.3gppnetwork.org.", tokenId=tokenID, priority = 1)




    def create_records_hss_1(hss_1_ip):
        DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='hss-1',record_type='A',record_data=hss_1_ip,tokenId=tokenID)

    def create_records_hss_2(hss_2_ip):
        DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='hss-2',record_type='A',record_data=hss_2_ip,tokenId=tokenID)

    def create_records_slf(slf_ip):
        DNSaaSClient.createRecord(domain_name='epc.mnc001.mcc001.3gppnetwork.org',record_name='slf',record_type='A',record_data=slf_ip,tokenId=tokenID)

