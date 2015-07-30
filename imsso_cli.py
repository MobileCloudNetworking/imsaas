from pbr.cmd import main

__author__ = 'gca'


import logging
from keystoneclient.v2_0.client import Client as KeystoneClient

logger=logging.getLogger(__name__)

class ImsSoCli(object):
    def __init__(self):
        self.config={}
        self.Util._read_properties(self.config)
        ks_args=Util._get_credentials(self.config)
        keystone = KeystoneClient(**ks_args)
        self.token=keystone.auth_token
        logger.info('instatiated IMS CLI with token %s' %self.token)

    def instantiate_ims(self):
        """

        :return:
        """
        pass

    def delete_ims(self):
        """

        :return:
        """
        pass


if __name__ == '__main__':
    imscli = ImsSoCli()


class Util(object):

    @staticmethod
    def _read_properties(self, props={}):
        with open('etc/imsso.properties', 'r') as f:
            for line in f:
                line = line.rstrip()

                if "=" not in line:
                    continue
                if line.startswith("#"):
                    continue

                k, v = line.split("=", 1)
                props[k] = v

    @staticmethod
    def _get_credentials(conf):
        # print "Fetch credentials from environment variables"
        creds = {}
        creds['tenant_name'] = conf.get('os_tenant', '')
        creds['username'] = conf.get('os_username', '')
        creds['password'] = conf.get('os_password', '')
        creds['auth_url'] = conf.get('os_auth_url', '')
        return creds


