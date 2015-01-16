from emm_exceptions import NotFoundException
from model.Entities import Service
from services.DatabaseManager import DatabaseManager
from services.Checker import check

__author__ = 'lto'


class ServiceOrchestrator:

    def __init__(self):
        pass

    @classmethod
    def create(cls, service_args):
        new_service = Service(**service_args)
        new_service.type = Service.__name__
        check(service=new_service)
        db = DatabaseManager()
        db.persist(new_service)
        return new_service

    @classmethod
    def delete(cls, id):
        db = DatabaseManager()
        try:
            service_to_remove = db.get_by_id(Service, id)
        except NotFoundException as e:
            raise e
        db.remove(service_to_remove)
        return service_to_remove


    @classmethod
    def update(cls, service_args, id):
        db = DatabaseManager()
        try:
            updated_service = db.get_by_id(Service, id)
        except NotFoundException as e:
            raise e
        updated_service.config = service_args.get('config') or updated_service.config
        updated_service.flavor = service_args.get('flavor') or updated_service.flavor
        updated_service.image = service_args.get('image') or updated_service.image
        updated_service.service_type = service_args.get('service_type') or updated_service.service_type
        updated_service.size = service_args.get('size') or updated_service.size
        check(service=updated_service)
        db.update(updated_service)
        return updated_service

    @classmethod
    def get(cls, id):
        db = DatabaseManager()
        try:
            service = db.get_by_id(Service, id)
        except NotFoundException as e:
            raise e
        return service

    @classmethod
    def get_all(cls):
        return DatabaseManager().get_all(Service)