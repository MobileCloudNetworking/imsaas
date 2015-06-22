#!/usr/bin/env python
# /*******************************************************************************
# * Copyright (C) 2013 FhG Fokus
# * 
# * This file is part of the OpenSDNCore project.
# ******************************************************************************/

import sys
import json
import os
import subprocess
import requests
import time

import shutil
import re
import httplib


def get_domain_id(domains_v, domain_str):
    for domain in domains_v:
        if domain["name"] == domain_str:
            print "Found: " + domain_str + " => ID: " + domain["id"]
            return domain["id"];


def download_domains_file(dns_server_ip):
    domains_file = open('domains', 'w')
    cmd = ['wget', '-O', '-', dns_server_ip + ':9001/v1/domains']
    ret = subprocess.call(cmd, stdout=domains_file)
    domains_file.close()


def download_records_file(dns_server_ip, domains_v, domain_str):
    records_file = open(domain_str, 'w')
    domain_id = get_domain_id(domains_v, domain_str)
    cmd = ['wget', '-O', '-', dns_server_ip + ':9001/v1/domains/' + domain_id + '/records']
    ret = subprocess.call(cmd, stdout=records_file)
    records_file.close()


def extract_domains_from_file(domains_file):
    domains_v = json.loads(domains_file.read())
    for domain in domains_v["domains"]:
        print domain["name"], domain["id"]
    return domains_v["domains"]


def extract_records_from_file(records_file):
    records_v = json.loads(records_file.read())
    for record in records_v["records"]:
        print record["name"], record["id"]
    return records_v["records"]


def get_domains(moniker_ip):
    headers = {'Content-type': 'application/json'}
    connection = httplib.HTTPConnection('%s:9001' % moniker_ip)
    connection.request('GET', '/v1/domains', headers)
    response = connection.getresponse()
    return response.read()


def filter_records_file(records_file_str, names_to_keep_list):
    remove_record_list = []

    records_file = open(records_file_str, 'r+w')
    records_v = json.loads(records_file.read())

    for record in records_v["records"]:
        record_fqdn = record["name"]
        record_id = record["id"]
        if not record_fqdn in names_to_keep_list:
            print record_fqdn + " will be filtered"
            remove_record_list.append(record)

    for record in remove_record_list:
        print 'Filtering ' + record["name"]
        records_v["records"].remove(record)

    records_file.seek(0)
    json.dump(records_v, records_file)
    records_file.truncate()
    records_file.close()


# TODO: Doesn't work yet,
#       CHECK ON THAT ONE
def add_domain(dns_server_ip, domain_str, ttl=None, email=None):
    if ttl is None:
        ttl = '3600'
    if email is None:
        email = 'lars.grebe@fokus.fraunhofer.de'

    url = str('http://' + dns_server_ip + ':9001/v1/domains')
    headers = {'content-type': 'application/json'}
    data = {'name': domain_str, 'ttl': ttl, 'email': email}
    data_json = json.dumps(data)

    print "Debug: ", data_json

    response = requests.post(url, data=data_json, headers=headers)
    if not response.ok:
        print "Error: Adding domain failed!"
        print response.content


def rm_domain(dns_server_ip, domains_v, domain_str):
    domain_id = get_domain_id(domains_v, domain_str)

    url = str('http://' + dns_server_ip + ':9001/v1/domains/' + domain_id)
    response = requests.delete(url)

    if not response.ok:
        print "Error: deletion failed!"


def get_domain_records(dns_server_ip, domains_v, domain_str):
    domain_id = get_domain_id(domains_v, domain_str)
    url = str('http://' + dns_server_ip + ':9001/v1/domains/' + domain_id + '/records')
    response = requests.get(url)
    if not response.ok:
        print "Error: Couldn't retreive domain records!"
        return []
    domain_records = json.loads(response.content)  # maybe only 'response.text' is provided!
    return domain_records["records"]


def add_domain_a_record(dns_server_ip, domains_v, domain_str, fqdn_str, ip_str):
    domain_id = get_domain_id(domains_v, domain_str)

    print "Trying to add ", fqdn_str, ip_str, " for id: ", domain_id

    url = str('http://' + dns_server_ip + ':9001/v1/domains/' + domain_id + '/records')

    data = {'name': fqdn_str, 'type': 'A', 'data': ip_str}
    data_json = json.dumps(data);

    headers = {'content-type': 'application/json'}

    print data_json

    response = requests.post(url, data=data_json, headers=headers)
    if not response.ok:
        print "Error: Adding domain record failed!"


def add_domain_srv_record(dns_server_ip, domains_v, domain_str, fqdn_str, ip_str):
    domain_id = get_domain_id(domains_v, domain_str)

    print "Trying to add ", fqdn_str, ip_str, " for id: ", domain_id

    url = str('http://' + dns_server_ip + ':9001/v1/domains/' + domain_id + '/records')

    data = {'type': 'SRV', 'name': fqdn_str, 'priority': 1, 'data': ip_str}
    data_json = json.dumps(data);

    headers = {'content-type': 'application/json'}

    print data_json

    response = requests.post(url, data=data_json, headers=headers)
    if not response.ok:
        print "Error: Adding domain record failed!"


def add_domain_naptr_record(dns_server_ip, domains_v, domain_str, fqdn_str, prio, ip_str):
    domain_id = get_domain_id(domains_v, domain_str)

    print "Trying to add ", fqdn_str, ip_str, " for id: ", domain_id

    url = str('http://' + dns_server_ip + ':9001/v1/domains/' + domain_id + '/records')

    data = {'type': 'NAPTR', 'name': fqdn_str, 'priority': prio, 'data': ip_str}
    data_json = json.dumps(data);

    headers = {'content-type': 'application/json'}

    print data_json

    response = requests.post(url, data=data_json, headers=headers)
    if not response.ok:
        print "Error: Adding domain record failed!"


def rm_domain_a_record(dns_server_ip, domains_v, domain_str, fqdn_str, record_v=None):
    domain_id = get_domain_id(domains_v, domain_str)
    if record_v is None:
        record_v = get_domain_records(dns_server_ip, domains_v, domain_str)

    record = None
    for r in record_v:
        if r["name"] == fqdn_str:
            record = r

    if not r:
        print "Error: Couldn't find A record for: " + fqdn_str
        return

    record_id = record["id"]

    print "Trying to remove ", fqdn_str, " for domain id: ", domain_id

    url = str('http://' + dns_server_ip + ':9001/v1/domains/' + domain_id + '/records/' + record_id)
    response = requests.delete(url)

    if not response.ok:
        print "Error: deletion failed!"


def rm_domain_srv_record(dns_server_ip, domains_v, domain_str, fqdn_str, record_v=None):
    domain_id = get_domain_id(domains_v, domain_str)
    if record_v is None:
        record_v = get_domain_records(dns_server_ip, domains_v, domain_str)

    record = None
    for r in record_v:
        if r["name"] == fqdn_str:
            record = r

    if not r:
        print "Error: Couldn't find SRV record for: " + fqdn_str
        return

    record_id = record["id"]

    print "Trying to remove ", fqdn_str, " for domain id: ", domain_id

    url = str('http://' + dns_server_ip + ':9001/v1/domains/' + domain_id + '/records/' + record_id)
    time.sleep(2)
    response = requests.delete(url)

    if not response.ok:
        print "Error: deletion failed!"


def rm_domain_naptr_record(dns_server_ip, domains_v, domain_str, fqdn_str, record_v=None):
    domain_id = get_domain_id(domains_v, domain_str)
    if record_v is None:
        record_v = get_domain_records(dns_server_ip, domains_v, domain_str)

    record = None
    for r in record_v:
        if r["name"] == fqdn_str:
            record = r

    if not r:
        print "Error: Couldn't find NAPTR record for: " + fqdn_str
        return

    record_id = record["id"]

    print "Trying to remove ", fqdn_str, " for domain id: ", domain_id

    url = str('http://' + dns_server_ip + ':9001/v1/domains/' + domain_id + '/records/' + record_id)
    time.sleep(2)
    response = requests.delete(url)

    if not response.ok:
        print "Error: deletion failed!"


###
# resolver_adapt_config - Use 'resolvconf' to influence the assemlence of
# /etc/resolv.conf.
#
# Usually 'resolvconf' is used to assemble the /etc/resolv.conf file.  The
# program 'resolvconf' will use DHCP information (hence, dynamically provided
# DNS information) to create the resolver file.
#
# This function will change information within /etc/network/interfaces and with
# this indirectly influence how the /etc/resolv.conf is assembled by
# 'resolvconf'.
# 
# This function assumes that the configuration of 'dhclient' is set up in a 
# way, that DHCP options:
# 
#   'domain-name', 'domain-name-servers', 'domain-search'
# 
# are removed from all interfaces.
#
def resolver_adapt_config(if_name, dns_server_ip, dns_server_ip_openstack, dns_domain_name, dns_domain_name_openstack):
    interfaces_file_name = '/etc/network/interfaces'
    head_file_name = '/etc/resolvconf/resolv.conf.d/head'
    search_str = '^iface ' + if_name + ' inet dhcp'
    # THIS VERSION USES THE /etc/resolvconf/resolv.conf.d/head file to keep the dns_server_ip at the very top
    # Yeah thats quite dirty...
    #ns_line     = '  dns-nameservers ' + dns_server_ip + ' ' + dns_server_ip_openstack + '\n'
    # dns_domain_name will be an array ...
    search_line = '  dns-search '
    for entry in dns_domain_name:
        search_line = search_line + entry + ' '
    search_line = search_line + ' ' + dns_domain_name_openstack + '\n'

    ## DEBUG

    # create backup
    shutil.copy2(interfaces_file_name, interfaces_file_name + '.bak')
    shutil.copy2(head_file_name, head_file_name + '.bak')
    # Do the dirty adding of our dns_name_server to the head file...
    with open(head_file_name, "a") as head_file:
        head_file.write(os.linesep)
        if dns_server_ip not in open(head_file_name).read():
            head_file.write("nameserver ")
            head_file.write(dns_server_ip)
        head_file.write(os.linesep)
    head_file.close()

    # open file and try to match 'search_str'
    interfaces_file = open(interfaces_file_name, 'rw+')
    match_idx = -1
    line_v = interfaces_file.readlines()
    for i in range(len(line_v)):
        line = line_v[i]
        m = re.search(search_str, line)

        # If found, break
        if m is not None:
            print "DEBUG: found search string"
            match_idx = i
            break

    # if found, insert special nameservers line and search line
    if match_idx != -1:
        print "DEBUG: inserting lines"
        #line_v.insert (match_idx + 1, ns_line)
        line_v.insert(match_idx + 2, search_line)

    interfaces_file.seek(0)
    interfaces_file.writelines(line_v)
    interfaces_file.close()

    # Restart network interface via 'initctl'
    #   Pray and hope!
    cmd_str = 'initctl restart network-interface INTERFACE=' + if_name
    ret = subprocess.call(cmd_str.split(' '))


def resolver_restore_backup(if_name):
    interfaces_file_name = '/etc/network/interfaces'
    backup_file_name = interfaces_file_name + '.bak'
    # Do not forget our dirty solution!!!
    head_backup_file_name = "/etc/resolvconf/resolv.conf.d/head.bak"

    if os.path.exists(backup_file_name):
        print "DEBUG: restoring backup file " + backup_file_name
        shutil.copy2(backup_file_name, interfaces_file_name)

        # Restart network interface via 'initctl'
        #   Pray and hope!
        cmd_str = 'initctl restart network-interface INTERFACE=' + if_name
        ret = subprocess.call(cmd_str.split(' '))
    else:
        print "Error: Can't restore backup file " + backup_file_name

    if os.path.exists(head_backup_file_name):
        print "DEBUG: restoring backup file " + head_backup_file_name
        shutil.copy2(head_backup_file_name, "/etc/resolvconf/resolv.conf.d/head")

        # Restart network interface via 'initctl'
        #   Pray and hope!
        cmd_str = 'initctl restart network-interface INTERFACE=' + if_name
        ret = subprocess.call(cmd_str.split(' '))
    else:
        print "Error: Can't restore backup file " + head_backup_file_name


def replace_resolver_file(dns_server_ip, dns_server_ip_openstack, dns_domain_names):
    resolver_file_name = '/etc/resolv.conf'

    shutil.copy2(resolver_file_name, resolver_file_name + '.bak')

    resolver_file = open(resolver_file_name, 'w')
    resolver_file.write('nameserver\t' + dns_server_ip + '\n')
    resolver_file.write('nameserver\t' + dns_server_ip_openstack + '\n')
    for entry in dns_domain_names:
        resolver_file.write('search\t' + entry + '\n')
    resolver_file.close()


def test():
    this_ip = utils.unit_get('private_address')
    dns_server_ip = utils.relation_get('private_address')

    dns_server_ip_file = open('dns_server_ip', 'w')
    dns_server_ip_file.write(dns_server_ip)
    dns_server_ip_file.close()

    dns_server_ip_openstack = '172.31.252.1'
    dns_domain_name = 'epc.mnc001.mcc001.3gppnetwork.org.'

    # Configure resolver
    replace_resolver_file(dns_server_ip, dns_server_ip_openstack, dns_domain_name)

    # Prepare 'domains'
    download_domains_file(dns_server_ip)
    domains_file = open('domains', 'r')
    domains = extract_domains_from_file(domains_file)
    domains_file.close()

    # Add domain A records, and save it to a file (name equeals domain)
    add_domain_a_record(dns_server_ip, domains, dns_domain_name, 'test' + '.' + dns_domain_name, this_ip)

    download_records_file(dns_server_ip, domains, dns_domain_name)

    # LATER THEN
    rm_domain_a_record(dns_server_ip, domains, dns_domain_name, 'test' + '.' + dns_domain_name, this_ip)
