# Copyright 2014 Technische Universitaet Berlin
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from SysUtil import SysUtil
from model.Entities import new_alchemy_encoder, Command
import json


__author__ = 'giuseppe'

def get_credentials():
    creds = {}
    ###Fetch Credentials from Configuration
    print "Fetch Credentials from SysUtil"
    conf = SysUtil().get_sys_conf()
    creds['tenant_name'] = conf.get('os_tenant', '')
    creds['username'] = conf.get('os_username', '')
    creds['password'] = conf.get('os_password', '')
    creds['auth_url'] = conf.get('os_auth_url', '')
    print 'Credentials: %s' % creds
    return creds

def get_token():
    from clients import keystone
    ###Init keystone client
    ksclient = keystone.Client()
    ###Get token from keystone
    token = ksclient.get_token()
    print "token: %s" % token
    return token

def get_endpoint(service_type, endpoint_type=None):
    from clients import keystone
    ###Init keystone client
    ksclient = keystone.Client()
    endpoint = ksclient.get_endpoint(service_type=service_type, endpoint_type=endpoint_type)
    return endpoint


class literal_unicode(unicode):
    pass


def literal_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')


def to_json(obj, _indent=4, _separators=(',', ': ')):
        return json.dumps(obj, cls=new_alchemy_encoder(), indent=_indent, separators=_separators)


def get_user_data(maas_ip, dnsaas_ip=None):
    commands = []
    commands.append(Command("#!/usr/bin/env bash"))
    commands.append(Command("apt-get install -y zabbix-agent;"))
    commands.append(Command(r"sed -i 's/^\(Server[ \t]*\)=[ \t]*[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*.*$/\1 =%s"%maas_ip+"/' /etc/zabbix/zabbix_agentd.conf"))
    commands.append(Command(r"sed -i 's/^\(ServerActive[ \t]*\)=[ \t]*[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*.*$/\1 =%s"%maas_ip+"/' /etc/zabbix/zabbix_agentd.conf"))
    commands.append(Command("sed -i 's/Hostname=/#Hostname=/g' /etc/zabbix/zabbix_agentd.conf;"))
    commands.append(Command("service zabbix-agent restart;"))
    if dnsaas_ip is not None:
        commands.append(Command("cat << EOF > /etc/resolv.conf"))
        commands.append(Command("search epc.mnc001.mcc001.3gppnetwork.org"))
        commands.append(Command("domain epc.mnc001.mcc001.3gppnetwork.org"))
        commands.append(Command("nameserver %s"%dnsaas_ip))
        commands.append(Command("EOF"))

    return commands


def write_time(value):
    res_file = open('/tmp/results.csv', 'w')
    res_file.write('%s;' % value)
    res_file.close()