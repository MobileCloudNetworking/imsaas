#!/usr/bin/env python

# This is a modified file from rel1 of OpenSDNCore adapterScripts!
# It will not modify the nameserver/resolv.conf!

# /*******************************************************************************
# * Copyright (C) 2013 FhG Fokus
# * 
# * This file is part of the OpenSDNCore project.
# ******************************************************************************/

# system imports
import os
import time, dns_utils


def create_records(this_ip, dns_server_ip, domains_string):
    domains_vec = domains_string.split(" ")

    host_names = ['icscf', 'icscf-cx']
    dns_sip_host_name = 'icscf'

    portnumber = '5060'
    dns_sip_entry_vec = []
    for entry in domains_vec:
        dns_sip_entry_vec.append('_sip.' + entry)
        dns_sip_entry_vec.append('_sip._udp.' + entry)
        dns_sip_entry_vec.append('_sip._tcp.' + entry)

    # 3. Prepare 'domains' file
    domains = dns_utils.get_domains(dns_server_ip)
    domains = dns_utils.extract_domains_from_file(domains)

    # Add domain SRV records ...
    for domain_name in domains_vec:
        for entry in dns_sip_entry_vec:
            # Only add the srv records relating to the current used domain!
            if entry.endswith(domain_name):
                dns_utils.add_domain_srv_record(dns_server_ip, domains, domain_name, entry,
                                                '0 ' + portnumber + ' ' + dns_sip_host_name + '.' + domain_name)


                # Do not forget to create the create the general open-ims.test. entry

    for entry in domains_vec:
        dns_utils.add_domain_a_record(dns_server_ip, domains, entry, entry, this_ip)
        # Then also add NAPTR entries!
        dns_utils.add_domain_naptr_record(dns_server_ip, domains, entry, entry, 10,
                                          '50 "s" "SIP+D2U" ""      _sip._udp.' + entry)
        time.sleep(1)
        dns_utils.add_domain_naptr_record(dns_server_ip, domains, entry, entry, 20,
                                          '50 "s" "SIP+D2T" ""      _sip._tcp.' + entry)

    # Add domain A records, and save it to a file (name equals domain)
    for domain_name in domains_vec:
        for host in host_names:
            dns_utils.add_domain_a_record(dns_server_ip, domains, domain_name, host + '.' + domain_name, this_ip)

    if os.path.exists('domains'):
        os.remove('domains')
