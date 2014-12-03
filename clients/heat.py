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

from util import util
from heatclient.client import Client as HeatClient
from heatclient.common import utils
from heatclient.common import template_utils
import heatclient.exc as exc
import json


class Client(object):
    def __init__(self):
        heat_args = util.get_credentials()
        heat_args['token'] = util.get_token()
        endpoint = util.get_endpoint(service_type='orchestration', endpoint_type='publicURL')
        self.client = HeatClient(version='1', endpoint=endpoint, **heat_args)
        #self.client = heat.Client(version='1', auth_url=auth_url, tenant_name=tenant_name, username=username, password=password, token = None)


    def deploy(self, name, template, parameters=None, environment = None, disable_rollback=None, timeout = None):
        kcargs = {
            'stack_name': name,
            'disable_rollback': not (bool('enable_rollback')),
            'parameters': utils.format_parameters(parameters),
            'template': template,
            #'files' : dict(list(tpl_files.items()) + list(env_files.items())),
            #'files' : dict(list(kwargs.get('environment_file').items())),
            'environment' : environment
        }
        print json.dumps(kcargs, indent=2)
        if timeout:
            kcargs['timeout_mins'] = timeout
        try:
            stack_details = self.client.stacks.create(**kcargs)
        except exc.HTTPNotFound:
            raise exc.CommandError('Stack already exists: %s' % name)
        return stack_details

    def delete(self, stack_id):
        fields = {'stack_id': stack_id}
        try:
            stack_details = self.client.stacks.delete(**fields)
            return stack_details
        except exc.HTTPNotFound as e:
            print(e)


    def show(self, stack_id, properties=[]):
        fields = {'stack_id': stack_id}
        try:
            stack = self.client.stacks.get(**fields)
        except exc.HTTPNotFound:
            raise exc.CommandError('Stack not found: %s' % fields['stack_id'])
        else:
            tmp_stack = stack.to_dict()
            if properties:
                return_stack = {}
                print "tmp_sack %s" % tmp_stack
                for property in properties:
                    if tmp_stack.get(property):
                        return_stack[property] = tmp_stack.get(property)
            else:
                return_stack = tmp_stack
        #list = heatClient.resources.list(stack_id)
        #return_stack.update(list)
        return return_stack


    def get_stack_id(self):
        return self.stack_id

    def list(self, args=None):
        kwargs = {}
        if args:
            kwargs = {'limit': args.get['limit'],
                      'marker': args.get['marker'],
                      'filters': utils.format_parameters(args.get['filters']),
                      'global_tenant': args.get['global_tenant'],
                      'show_deleted': args.get['show_deleted']}
        stacks = self.client.stacks.list(**kwargs)
        fields = ['id', 'stack_name', 'stack_status', 'creation_time']
        #utils.print_list(stacks, fields)
        return stacks

    def list_resources(self, stack_id):
        resources_raw = self.client.resources.list(stack_id)
        resources = []
        for resource_raw in resources_raw:
            resources.append(resource_raw.to_dict())
        return resources

    def list_resource_ids(self, stack_id):
        resources_raw = self.client.resources.list(stack_id)
        resource_ids = []
        for resource_raw in resources_raw:
            resource_id = resource_raw.to_dict().get('physical_resource_id')
            if resource_id:
                resource_ids.append(resource_id)
        return resource_ids

    def list_nested_resource_ids(self, stack_id):
        resources_raw = self.client.resources.list(stack_id)
        resource_ids = []
        for resource_raw in resources_raw:
            resource_id = resource_raw.to_dict().get('physical_resource_id')
            if resource_id:
                nested_resources_raw = self.client.resources.list(resource_id)
                for nested_resource_raw in nested_resources_raw:
                    resource_type = nested_resource_raw.to_dict().get('resource_type')
                    if resource_type == 'OS::Nova::Server':
                        nested_resource_id = nested_resource_raw.to_dict().get('physical_resource_id')
                        if nested_resource_id:
                            resource_ids.append(nested_resource_id)
        return resource_ids

    def get_resources(self, stack_id, resource_names=[]):
        resources = {}
        for resource_name in resource_names:
            try:
                resource = self.client.resources.get(stack_id, resource_name)
                resources[resource_name] = resource.to_dict()
            except:
                resources[resource_name] = None
        return resources

    def get_environment_and_file(self, env_path):
        env_files, env = template_utils.process_environment_and_files(env_path=env_path)
        print "env: %s" % env
        print "env files: %s" % env_files
        return env, env_files
