from model.Entities import Network, Subnet
from services.DatabaseManager import DatabaseManager

__author__ = 'lto'


class NetworkOrchestrator:

    def __init__(self):
        pass

    @classmethod
    def get_all_networks(cls):
        db = DatabaseManager()
        networks = db.get_all(Network)
        return networks


    @classmethod
    def get_all_subnets(cls):
        db = DatabaseManager()
        networks = db.get_all(Subnet)
        return networks
