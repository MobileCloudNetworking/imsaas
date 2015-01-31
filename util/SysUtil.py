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


import json
import logging
import os
from clients.neutron import Client as NeutronClient
from clients.nova import Client as NovaClient

from model.Entities import Configuration, new_alchemy_encoder

import FactoryAgent as FactoryAgent

PATH = os.environ.get('OPENSHIFT_REPO_DIR', '.')

__author__ = 'lto'

global sys_config
sys_config = Configuration()


logger = logging.getLogger(__name__)

class SysUtil:

    def print_logo(self):
        logger.info('Welcome: \n' +
                         ' _______  __                __    __        _______            __  __         _______\n'
                         '|    ___||  |.---.-..-----.|  |_ |__|.----.|   |   |.-----..--|  ||__|.---.-.|   |   |.---.-..-----..---.-..-----..-----..----.\n'
                         '|    ___||  ||  _  ||__ --||   _||  ||  __||       ||  -__||  _  ||  ||  _  ||       ||  _  ||     ||  _  ||  _  ||  -__||   _|\n'
                         '|_______||__||___._||_____||____||__||____||__|_|__||_____||_____||__||___._||__|_|__||___._||__|__||___._||___  ||_____||__|\n'
                         '                                                                                                           |_____|             \n'
        )

    def _read_properties(self, props={}):
        with open('%s/etc/imsso.properties' % PATH, 'r') as f:
            for line in f:
                line = line.rstrip()

                if "=" not in line:
                    continue
                if line.startswith("#"):
                    continue

                k, v = line.split("=", 1)
                props[k] = v

    def init_sys(self):
        logger.info("Starting the System")
        logger.debug('Retrieving the System Configurations')
        sys_config.props = {}
        sys_config.name = 'SystemConfiguration'
        self._read_properties(sys_config.props)
        logger.debug('getting the DbManager')
        db = FactoryAgent.FactoryAgent().get_agent(file_name=sys_config.props['database_manager'])
        if sys_config.props['create_tables'] == 'True':
            db.create_tables()
        old_cfg = db.get_by_name(Configuration, sys_config.name)
        if old_cfg:
            old_cfg[0].props = sys_config.props
            db.update(old_cfg[0])
        else:
            db.persist(sys_config)

        for net in get_networks():
            db.persist(net)

        for key in get_keys():
            db.persist(key)

        for flavor in get_flavors():
            db.persist(flavor)

        for image in get_images():
            db.persist(image)

        # for port in get_ports():
        #     db.persist(port)

        self.print_logo()

    def get_sys_conf(self):
        props = {}
        self._read_properties(props)
        return props


def get_credentials():
    # print "Fetch credentials from environment variables"
    creds = {}
    # creds['tenant_name'] = os.environ.get('OS_TENANT_NAME', '')
    # creds['username'] = os.environ.get('OS_USERNAME', '')
    # creds['password'] = os.environ.get('OS_PASSWORD', '')
    # creds['auth_url'] = os.environ.get('OS_AUTH_URL', '')
    # print 'Credentials: %s' % creds
    # ##Fetch Credentials from Configuration
    logger.debug("Fetch Credentials from SysUtil")
    conf = SysUtil().get_sys_conf()
    #conf = DatabaseManager().get_by_name(Configuration, "SystemConfiguration")[0]
    #print "props: %s" % conf.props
    creds['tenant_name'] = conf.get('os_tenant', '')
    creds['username'] = conf.get('os_username', '')
    creds['password'] = conf.get('os_password', '')
    creds['auth_url'] = conf.get('os_auth_url', '')
    logger.debug('Credentials: %s' % creds)
    return creds


def get_token():
    from clients import keystone
    # ##Init keystone client
    ksclient = keystone.Client()
    ###Get token from keystone
    token = ksclient.get_token()
    logger.debug("token: %s" % token)
    return token


def get_endpoint(service_type, endpoint_type=None):
    from clients import keystone
    # ##Init keystone client
    ksclient = keystone.Client()
    endpoint = ksclient.get_endpoint(service_type=service_type, endpoint_type=endpoint_type)
    return endpoint


def get_networks():
    nc = NeutronClient(get_endpoint('network'), get_token())
    return nc.get_networks()

def get_ports():
    nc = NeutronClient(get_endpoint('network'), get_token())
    return nc.get_ports()


def get_images():
    novaClient = NovaClient(sys_config.props)
    return novaClient.get_images()

def get_keys():
    novaClient = NovaClient(sys_config.props)
    return novaClient.get_keys()

def get_flavors():
    novaClient = NovaClient(sys_config.props)
    return novaClient.get_flavors()

def translate(value, mapping, err_msg=None):
    try:
        return mapping[value]
    except KeyError as ke:
        if err_msg:
            raise KeyError(err_msg % value)
        else:
            raise ke

class literal_unicode(unicode): pass


def literal_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')


def to_json(obj, _indent=4, _separators=(',', ': ')):
    return json.dumps(obj, cls=new_alchemy_encoder(), indent=_indent, separators=_separators)