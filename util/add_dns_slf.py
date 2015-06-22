#!/usr/bin/env python
# /*******************************************************************************
# * Copyright (C) 2013 FhG Fokus
# * 
# * This file is part of the OpenSDNCore project.
# ******************************************************************************/
# system imports
import sys, os, subprocess, getopt
import time

# local imports
import dns_utils


def create_records(this_ip, dns_server_ip, domains_string):
    domains_vec = domains_string.split(" ")

    # Use the name defined in the config, since we may want to deploy multiple instances!
    # So do not get problems with the dns...
    host_name = "slf"

    # Prepare 'domains'
    domains = dns_utils.get_domains(dns_server_ip)
    domains = dns_utils.extract_domains_from_file(domains)

    # Add domain A records, and save it to a file (name equals domain)
    for entry in domains_vec:
        dns_utils.add_domain_a_record(dns_server_ip, domains, entry, host_name + '.' + entry, this_ip)

    #
    # # Download the complete records files
    # for entry in domains_vec:
    #     dns_utils.download_records_file(dns_server_ip, domains, entry)
    #
    # # Prepare a list of entries relating to our charm
    #
    # host_names_fqdn = []
    # for entry in domains_vec:
    #     host_names_fqdn.append(host_name + '.' + entry)
    #
    # # Delete all entries in all record files not relating to our charm
    # for entry in domains_vec:
    #     dns_utils.filter_records_file(entry, host_names_fqdn)
    #
    # if os.path.exists('domains'):
    #     os.remove('domains')
