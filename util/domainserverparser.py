#!/usr/bin/env python

# This is a modified file from rel1 of OpenSDNCore adapterScripts!
# renamed the servers / domains file to moniker_servers / moniker_domains
# to avoid influence on add_dns pythons scripts of the ims services ;)

#/*******************************************************************************
# * Copyright (C) 2013 FhG Fokus
# * 
# * This file is part of the OpenSDNCore project.
# ******************************************************************************/

# This script contains methods used by the moniker install script, it allows to parse
# specific values out of the json files.

import json


def check_if_servers_empty():
    servers_file = open('moniker_servers', 'r')
    data = json.loads(servers_file.read())
    if data["servers"]:
        print "servers not empty"


def check_if_domains_empty():
    domains_file = open('moniker_domains', 'r')
    data = json.loads(domains_file.read())
    if data["domains"]:
        print "domains not empty"


def parse_domain_id_from_file(n):
    domains_file = open('moniker_domains', 'r')
    data = json.loads(domains_file.read())
    print data["domains"][n]["id"]


def parse_domain_id(n, domains_file):
    print "parsing domain_id in domains_file %s" %domains_file
    data = json.loads(domains_file)
    print data["domains"][n]["id"]
    return data["domains"][n]["id"]


def parse_server_name(n):
    servers_file = open ('moniker_servers', 'r')
    data = json.loads (servers_file.read())
    print data["servers"][n]["name"]
