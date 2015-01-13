__author__ = 'lto'

from util import FactoryAgent as FactoryAgent

if __name__ == '__main__':

    dep = FactoryAgent.FactoryAgent().get_agent(file_name='Deployer')