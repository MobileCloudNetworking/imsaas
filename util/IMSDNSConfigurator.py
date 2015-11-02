__author__ = 'gca'

import os, logging

logger = logging.getLogger(__name__)


class ImsDnsClient(object):
    def __init__(self, dnsaas):
        self.dnsaas = dnsaas
        self.__domain_name = 'epc.mnc001.mcc001.3gppnetwork.org'
        self.__admin_email = 'admin@mcn.pt'
        self.tokenID = os.environ['OS_AUTH_TOKEN']
        self.dns_ip =  os.environ['DNSAAS_API']
        #self.dns_ip = self.dnsaas.get_address()
        logger.info("Initialized the IMS DNS Client")

        # In case of a standalone topology we need to create also the domains
        self.dnsaas.create_domain(domain_name=self.__domain_name, email=self.__admin_email, ttl=3600,
                                  token=self.tokenID)
        logger.info("Initialized the DNS")

        self.dnsaas.create_record(domain_name=self.__domain_name, record_name='ns', record_type='A',
                                  record_data=self.dns_ip, token=self.tokenID)
        self.dnsaas.create_record(domain_name=self.__domain_name, record_name='dns', record_type='A',
                                  record_data=self.dns_ip, token=self.tokenID)
        self.dnsaas.create_record(domain_name=self.__domain_name, record_name="", record_type='NAPTR',
                                  record_data="10 50 \"s\" \"SIP+D2U\" \"\" _sip._udp", token=self.tokenID,
                                  priority=10)
        self.dnsaas.create_record(domain_name=self.__domain_name, record_name="", record_type='NAPTR',
                                  record_data="20 50 \"s\" \"SIP+D2U\" \"\" _sip._tcp", token=self.tokenID,
                                  priority=10)

        logger.info("Initialized the IMS DNS Client")

    def create_records_cscfs(self, cscfs_ip, hostname=None):
        logger.debug("Creating records for the cscfs %s"%cscfs_ip)
        self.__create_records_icscf(cscfs_ip)
        self.__create_records_pcscf(cscfs_ip)
        self.__create_records_scscf(cscfs_ip)

    def __create_records_pcscf(self, pcscf_ip):
        logger.info("Creating records for the pcscf %s with domain_name %s, "
                     "record_data %s, tokenId %s"%(pcscf_ip,self.__domain_name, pcscf_ip, self.tokenID))
        self.dnsaas.create_record(domain_name=self.__domain_name, record_name='pcscf', record_type='A',
                                  record_data=pcscf_ip, token=self.tokenID)
        self.dnsaas.create_record(domain_name=self.__domain_name, record_name='pcscf-rx',
                                  record_type='A', record_data=pcscf_ip, token=self.tokenID)
        self.dnsaas.create_record(domain_name=self.__domain_name, record_name='pcscf-rxrf',
                                  record_type='A', record_data=pcscf_ip, token=self.tokenID)
        self.dnsaas.create_record(domain_name=self.__domain_name, record_name='pcscf-rf',
                                  record_type='A', record_data=pcscf_ip, token=self.tokenID)
        self.dnsaas.create_record(self.__domain_name, "_sip.pcscf", "SRV",
                                  "0 4060 pcscf.epc.mnc001.mcc001.3gppnetwork.org.", token=self.tokenID, priority=1)
        self.dnsaas.create_record(self.__domain_name, "_sip._tcp.pcscf", "SRV",
                                  "0 4060 pcscf.epc.mnc001.mcc001.3gppnetwork.org.", token=self.tokenID, priority=1)

    def __create_records_icscf(self, icscf_ip):
        logger.info("Creating records for the icscf %s with domain_name %s, "
                     "record_data %s, tokenId %s"%(icscf_ip,self.__domain_name, icscf_ip, self.tokenID))
        self.dnsaas.create_record(domain_name=self.__domain_name, record_name='icscf', record_type='A',
                                  record_data=icscf_ip, token=self.tokenID)
        self.dnsaas.create_record(domain_name=self.__domain_name, record_name='icscf-cx',
                                  record_type='A', record_data=icscf_ip, token=self.tokenID)
        self.dnsaas.create_record(self.__domain_name, "_sip.icscf", "SRV",
                                  "0 5060 icscf.epc.mnc001.mcc001.3gppnetwork.org.", token=self.tokenID, priority=1)
        self.dnsaas.create_record(self.__domain_name, "_sip._udp.icscf", "SRV",
                                  "0 5060 icscf.epc.mnc001.mcc001.3gppnetwork.org.", token=self.tokenID, priority=1)
        self.dnsaas.create_record(self.__domain_name, "_sip._tcp.icscf", "SRV",
                                  "0 5060 icscf.epc.mnc001.mcc001.3gppnetwork.org.", token=self.tokenID, priority=1)
        self.dnsaas.create_record(self.__domain_name, "_sip._udp", "SRV",
                                  "0 5060 epc.mnc001.mcc001.3gppnetwork.org.", token=self.tokenID, priority=1)
        self.dnsaas.create_record(self.__domain_name, "_sip._tcp", "SRV",
                                  "0 5060 epc.mnc001.mcc001.3gppnetwork.org.", token=self.tokenID, priority=1)
        self.dnsaas.create_record(self.__domain_name, "_sip", "SRV",
                                  "0 5060 epc.mnc001.mcc001.3gppnetwork.org.", token=self.tokenID, priority=1)
        # TODO change
        self.dnsaas.create_record(domain_name=self.__domain_name, record_name='', record_type='A',
                                  record_data=icscf_ip, token=self.tokenID)

    def __create_records_scscf(self, scscf_ip):
        logger.info("Creating records for the scscf %s with domain_name %s, "
                     "record_data %s, tokenId %s"%(scscf_ip,self.__domain_name, scscf_ip, self.tokenID))
        self.dnsaas.create_record(domain_name=self.__domain_name, record_name='scscf', record_type='A',
                                  record_data=scscf_ip, token=self.tokenID)
        self.dnsaas.create_record(domain_name=self.__domain_name, record_name='scscf-cx',
                                  record_type='A', record_data=scscf_ip, token=self.tokenID)
        self.dnsaas.create_record(domain_name=self.__domain_name, record_name='scscf-cxrf',
                                  record_type='A', record_data=scscf_ip, token=self.tokenID)
        self.dnsaas.create_record(self.__domain_name, "_sip.scscf", "SRV",
                                  "0 6060 scscf.epc.mnc001.mcc001.3gppnetwork.org.", token=self.tokenID, priority=1)
        self.dnsaas.create_record(self.__domain_name, "_sip._tcp.scscf", "SRV",
                                  "0 6060 scscf.epc.mnc001.mcc001.3gppnetwork.org.", token=self.tokenID, priority=1)
        self.dnsaas.create_record(self.__domain_name, "_sip._udp.scscf", "SRV",
                                  "0 6060 scscf.epc.mnc001.mcc001.3gppnetwork.org.", token=self.tokenID, priority=1)

    def create_records_hss(self, hss_ip, hss_hostname):
        logger.info("Creating records for the hss %s with domain_name %s, "
                     "record_data %s, tokenId %s"%(hss_hostname, self.__domain_name, hss_ip, self.tokenID))
        self.dnsaas.create_record(domain_name='epc.mnc001.mcc001.3gppnetwork.org', record_name=hss_hostname,
                                  record_type='A',
                                  record_data=hss_ip, token=self.tokenID)

    def create_records_slf(self, slf_ip, hostname=None):
        logger.info("Creating records for the slf %s with domain_name %s, "
                     "record_data %s, tokenId %s"%(slf_ip, self.__domain_name, slf_ip, self.tokenID))
        self.dnsaas.create_record(domain_name='epc.mnc001.mcc001.3gppnetwork.org', record_name='slf', record_type='A',
                                  record_data=slf_ip, token=self.tokenID)

    def create_records_test(self, test_ip, hostname=None):
        print "testing dns entry with ip %s" % test_ip

    def configure_dns_entry(self, service_type):
        return {
            'hss': self.create_records_hss,
            'slf': self.create_records_slf,
            'dra': self.create_records_slf,
            'cscfs': self.create_records_cscfs,
            'test': self.create_records_test,
        }[service_type]


