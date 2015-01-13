__author__ = 'mpa'


from swiftclient import client as swiftclient

if __name__ == '__main__':

    authurl = 'http://80.96.122.48:8080/v1'
    #authurl = 'http://80.96.122.48:8080/v1/AUTH_fba35e226f4441c6b3b8bbd276f5d41a'
    user = 'services'
    tenant_name = 'services'
    password = 'nub0m3d1@'
    scl = swiftclient.Connection(authurl=authurl, user=user, tenant_name=tenant_name, key=password)
    print scl.get_account()
    print scl.token