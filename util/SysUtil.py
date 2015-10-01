import json
import logging
import os
from sqlalchemy.exc import IntegrityError

from clients.neutron import Client as NeutronClient
from clients.nova import Client as NovaClient
from model.Entities import Configuration, new_alchemy_encoder, Network, Key, Image, Flavor, Quotas
import FactoryAgent as FactoryAgent


PATH = os.environ.get('BUNDLE_DIR', '.')


__author__ = 'lto'

global sys_config
sys_config = Configuration()

logger = logging.getLogger(__name__)


class SysUtil:
    def print_logo(self):
        logger.info('\n' +
                    '$$$$$$\ $$\      $$\  $$$$$$\   $$$$$$\   $$$$$$\ \n'
                    '\_$$  _|$$$\    $$$ |$$  __$$\ $$  __$$\ $$  __$$\n'
                    '  $$ |  $$$$\  $$$$ |$$ /  \__|$$ /  \__|$$ /  $$\n'
                    '  $$ |  $$\$$\$$ $$ |\$$$$$$\  \$$$$$$\  $$ |  $$ |\n'
                    '  $$ |  $$ \$$$  $$ | \____$$\  \____$$\ $$ |  $$ |\n'
                    '  $$ |  $$ |\$  /$$ |$$\   $$ |$$\   $$ |$$ |  $$ |\n'
                    '$$$$$$\ $$ | \_/ $$ |\$$$$$$  |\$$$$$$  | $$$$$$  |\n'
                    '\______|\__|     \__| \______/  \______/  \______/ \n'
        )

    def _read_properties(self, props={}):
        with open('%s/etc/imsso.properties' % PATH, 'r') as f:
            logger.debug("Using %s/emm.properties file" % PATH)
            for line in f:
                line = line.rstrip()

                if "=" not in line:
                    continue
                if line.startswith("#"):
                    continue

                k, v = line.split("=", 1)
                props[k] = v

    def init_sys(self):
        sys_config.props = {}
        sys_config.name = 'SystemConfiguration'
        self._read_properties(sys_config.props)
        logging.basicConfig(format='%(asctime)s_%(process)d:%(pathname)s:%(lineno)d [%(levelname)s] %(message)s', level=sys_config.props['log_level'])
        logger.info("Starting the System")
        logger.debug('Creating and removing the tables')
        db = FactoryAgent.FactoryAgent().get_agent(agent=sys_config.props['database_manager'])
        if sys_config.props['create_tables'] == 'True':
            db.create_tables()
        old_cfg = db.get_by_name(Configuration, sys_config.name)
        if old_cfg:
            old_cfg[0].props = sys_config.props
            db.update(old_cfg[0])
        else:
            db.persist(sys_config)

        try:
            #Persist and update networks on database
            nets = get_networks()
            #remove old networks
            available_network_names = [net.name for net in nets]
            persisted_nets = db.get_all(Network)
            for persisted_net in persisted_nets:
                if persisted_net.name not in available_network_names:
                    db.remove(persisted_net)
            #update existing networks
            for net in nets:
                nets = db.get_by_name(Network, net.name)
                # if len(nets) >= 1:
                #     existing_net = nets[0]
                #     net.id = existing_net.id
                #     for subnet in net.subnets:
                #         for existing_subnet in existing_net.subnets:
                #             if subnet.name == existing_subnet.name:
                #                 subnet.id = existing_subnet.id
                #                 existing_subnet = subnet
                #                 db.update(existing_subnet)
                #     existing_net = net
                #     db.update(existing_net)
                # else:
                try:
                    db.persist(net)
                except IntegrityError, exc:
                    logger.warning('Network \"%s\" is already persisted on the Database.' % net.name)
            #Persist and update keys on database
            keys = get_keys()
            #remove old keys
            available_key_names = [key.name for key in keys]
            persisted_keys = db.get_all(Key)
            for persisted_key in persisted_keys:
                if persisted_key.name not in available_key_names:
                    db.remove(persisted_key)
            #update existing keys
            for key in keys:
                keys = db.get_by_name(Key, key.name)
                if len(keys) >= 1:
                    existing_key = keys[0]
                    key.id = existing_key.id
                    existing_key = key
                    db.update(existing_key)
                else:
                    try:
                        db.persist(key)
                    except IntegrityError, exc:
                        logger.warning('Key \"%s\" is already persisted on the Database.' % key.name)

            #Persist and update flavors on database
            flavors = get_flavors()
            #remove old flavors
            available_flavor_names = [flavor.name for flavor in flavors]
            persisted_flavors = db.get_all(Flavor)
            for persisted_flavor in persisted_flavors:
                if persisted_flavor.name not in available_flavor_names:
                    db.remove(persisted_flavor)
            #update existing flavors
            for flavor in flavors:
                flavors = db.get_by_name(Flavor, flavor.name)
                if len(flavors) >= 1:
                    existing_flavor = flavors[0]
                    flavor.id = existing_flavor.id
                    existing_flavor = flavor
                    db.update(existing_flavor)
                else:
                    try:
                        db.persist(flavor)
                    except IntegrityError, exc:
                        logger.warning('Flavor \"%s\" is already persisted on the Database. Trigger update.' % flavor.name)

            images = get_images()
            #remove old images
            available_image_names = [image.name for image in images]
            persisted_images = db.get_all(Image)
            for persisted_image in persisted_images:
                if persisted_image.name not in available_image_names:
                    db.remove(persisted_image)
            #update existing images
            for image in images:
                images = db.get_by_name(Image, image.name)
                if len(images) >= 1:
                    existing_image = images[0]
                    image.id = existing_image.id
                    existing_image = image
                    db.update(existing_image)
                else:
                    try:
                        db.persist(image)
                    except IntegrityError, exc:
                        logger.warning('Image \"%s\" is already persisted on the Database. Trigger update.' % image.name)

            all_quotas = db.get_all(Quotas)
            all_quotas_tenants = [quotas.tenant_id for quotas in all_quotas]
            new_quotas = get_quotas()
            #update existing quotas
            for quotas in all_quotas:
                if new_quotas.tenant_id in all_quotas_tenants:
                    new_quotas.id = quotas.id
                    quotas = new_quotas
                    db.update(quotas)
                else:
                    try:
                        db.persist(new_quotas)
                    except IntegrityError, exc:
                        logger.warning('Network \"%s\" are already persisted on the Database. Trigger update.' % get_quotas())
                        db.update(get_quotas())
        except Exception, exc:
            logger.exception(exc.message)
            raise

        # for port in get_ports():
        # db.persist(port)

        self.print_logo()

    def get_sys_conf(self):
        props = {}
        self._read_properties(props)
        return props


def get_networks():
    nc = NeutronClient(get_endpoint('network', region_name=sys_config.props['os_region_name']), get_token())
    return nc.get_networks()


def get_ports():
    nc = NeutronClient(get_endpoint('network', region_name=sys_config.props['os_region_name']), get_token())
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


def get_quotas():
    novaClient = NovaClient(sys_config.props)
    return novaClient.get_quotas()


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
    # conf = DatabaseManager().get_by_name(Configuration, "SystemConfiguration")[0]
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
    # ##Get token from keystone
    token = ksclient.get_token()
    logger.debug("token: %s" % token)
    return token


def get_endpoint(service_type, endpoint_type=None,region_name=None):
    from clients import keystone
    # ##Init keystone client
    ksclient = keystone.Client()
    endpoint = ksclient.get_endpoint(service_type=service_type, endpoint_type=endpoint_type, region_name=region_name)
    logger.debug("endpoint for service_type %s is %s" %(service_type,endpoint,))
    return endpoint


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
