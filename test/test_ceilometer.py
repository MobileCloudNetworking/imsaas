__author__ = 'micha'

from clients.ceilometer import Client as CeiloClient

if __name__ == '__main__':
    client = CeiloClient()
    print client.get_statitics(resource_id='8ada93a2-6cbb-43f7-9c4f-6c6857', meter_name='cpu_util', period=60)
