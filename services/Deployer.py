__author__ = 'mpa'

from util.Deployer import Deployer as ABCDeployer
from clients.heat import Client as HeatClient
from services import TemplateManager


class Deployer(ABCDeployer):

    def __init__(self):
        self.heatclient = HeatClient()

    def deploy(self, topology):
        print "Start Deploying"
        name, template = TemplateManager.get_template(topology)
        print "stack name: %s" % name
        print "template: %s" % template
        stack_details = self.heatclient.deploy(name=name, template=template)
        print "stack details after deploy: %s" % stack_details
        try:
            stack_id = stack_details['stack']['id']
            print "stack id: %s" % stack_id
        except KeyError, exc:
            print KeyError
            print exc
            stack_id = "None"

        print "resources: %s" % self.heatclient.list_resources(stack_id)
        print "resource ids: %s" % self.heatclient.list_resource_ids(stack_id)

        return stack_id

    def dispose(self, stack_id):
        stack_details = self.heatclient.delete(stack_id)
        print "stack details after delete: %s" % stack_details
        return stack_details

    def test(self):
        print 'yess'