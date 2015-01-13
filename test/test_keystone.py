from clients import heat, keystone

__author__ = 'mpa'

if __name__ == '__main__':
    ksclient = keystone.Client()
    print 'token: %s' % ksclient.get_token()
    endpoint = ksclient.get_endpoint()
    print 'endpoint: %s' % ksclient.get_endpoint()

