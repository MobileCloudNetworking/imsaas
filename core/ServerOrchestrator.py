from model.Entities import Image, Flavor, Key
from services.DatabaseManager import DatabaseManager

__author__ = 'mpa'


class ServerOrchestrator:

    def __init__(self):
        pass

    @classmethod
    def get_all_images(cls):
        db = DatabaseManager()
        images = db.get_all(Image)
        return images

    @classmethod
    def get_all_flavors(cls):
        db = DatabaseManager()
        flavors = db.get_all(Flavor)
        return flavors

    @classmethod
    def get_all_keys(cls):
        db = DatabaseManager()
        keys = db.get_all(Key)
        return keys
