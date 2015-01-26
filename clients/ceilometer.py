#!/usr/bin/python
# Copyright 2014 Technische Universitaet Berlin
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
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
__author__ = 'mpa'

from ceilometerclient import client
from util import SysUtil


class Client(object):
    def __init__(self):
        creds = SysUtil.get_credentials()
        creds['os_auth_token'] = SysUtil.get_token()
        #creds['token'] = util.get_token()
        #creds['ceilometer_url'] = util.get_endpoint(service_type='metering',endpoint_type='publicURL')
        self.cmclient = client.get_client('2', **creds)

    def get_last_sample_value(self, resource_id, meter_name):
        query = [dict(field='resource_id', op='eq', value=resource_id)]
        samples = self.cmclient.samples.list(meter_name=meter_name, limit=1, q=query)
        if samples:
            return samples[0]._info['counter_volume']
        else:
            False

    def get_statitics(self, resource_id, meter_name, period, aggregate='avg'):
        query = [dict(field='resource_id', op='eq', value=resource_id)]
        statistic = self.cmclient.statistics.list(meter_name=meter_name, q=query, period=period, aggregates = [{'func':aggregate}], groupby = ['resource_id'])
        item_value = None
        if statistic:
            item_value = statistic[-1]._info.get('aggregate').get('avg')
        return item_value

    def get_last_sample_values(self, resource_id, meter_name, limit=1):
        query = [dict(field='resource_id', op='eq', value=resource_id)]
        samples = self.cmclient.samples.list(meter_name=meter_name, limit=limit, q=query)
        values = []
        i = 1
        for sample in samples:
            #values.append(sample)
            values.append(
                {'sample_%s' % i: {'timestamp': sample._info['timestamp'], 'value': sample._info['counter_volume']}})
            i += 1
        return values

    def get_meters(self):
        return self.cmclient.meters.list()
