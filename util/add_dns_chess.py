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
import dns_utils


def create_records(this_ip, dns_server_ip, domains_string, host_name):
    domains_vec = domains_string.split(" ")

    # Prepare 'domains'
    domains = dns_utils.get_domains(dns_server_ip)
    domains = dns_utils.extract_domains_from_file(domains)

    # Add domain A records, and save it to a file (name equals domain)
    for entry in domains_vec:
        dns_utils.add_domain_a_record(dns_server_ip, domains, entry, host_name + '.' + entry, this_ip)

    if os.path.exists('domains'):
        os.remove('domains')
