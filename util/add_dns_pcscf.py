#!/usr/bin/env python

# This is a modified file from rel1 of OpenSDNCore adapterScripts!
# It will not modify the nameserver/resolv.conf!

# /*******************************************************************************
# * Copyright (C) 2013 FhG Fokus
# * 
# * This file is part of the OpenSDNCore project.
# ******************************************************************************/

# system imports
import sys, os, subprocess, getopt
import time

import dns_utils


def create_records(this_ip, dns_server_ip, domains_string):
    domains_vec = domains_string.split(" ")

    host_names = ['pcscf', 'pcscf-rx', 'pcscf-rxrf', 'pcscf-rf']
    dns_sip_host_name = 'pcscf'
    portnumber = '4060'
    dns_sip_entry_vec = []
    for entry in domains_vec:
        dns_sip_entry_vec.append('_sip.' + dns_sip_host_name + '.' + entry)
        dns_sip_entry_vec.append('_sip._udp.' + dns_sip_host_name + '.' + entry)
        dns_sip_entry_vec.append('_sip._tcp.' + dns_sip_host_name + '.' + entry)

    # Prepare 'domains'
    domains = dns_utils.get_domains(dns_server_ip)
    domains = dns_utils.extract_domains_from_file(domains)

    for domain_name in domains_vec:
        for host in host_names:
            dns_utils.add_domain_a_record(dns_server_ip, domains, domain_name, host + '.' + domain_name, this_ip)

        # Add domain srv records ...

    for domain_name in domains_vec:
        for entry in dns_sip_entry_vec:
            # Only add the srv records relating to the current used domain!
            if entry.endswith(domain_name):
                dns_utils.add_domain_srv_record(dns_server_ip, domains, domain_name, entry,
                                                '0 ' + portnumber + ' ' + dns_sip_host_name + '.' + domain_name)

    if os.path.exists('domains'):
        os.remove('domains')
