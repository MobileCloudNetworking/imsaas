from emm_exceptions import NotFoundException
from services.DatabaseManager import DatabaseManager
from model.Entities import Rule, SecurityGroup
from services.Checker import check

__author__ = 'lto'


class SecurityGroupOrchestrator:
    def __init__(self):
        pass

    @classmethod
    def create(cls, secgroup_args):
        _sec_rules = secgroup_args.get("rules")
        _new_sec_rules = []
        for _sec_rule_args in _sec_rules:
            _new_sec_rule = Rule(**_sec_rule_args)
            _new_sec_rules.append(_new_sec_rule)
        new_secgroup = SecurityGroup(name=secgroup_args.get('name'), rules=_new_sec_rules)
        check(security_group=new_secgroup)
        db = DatabaseManager()
        db.persist(new_secgroup)
        return new_secgroup

    @classmethod
    def get(cls, id):
        db = DatabaseManager()
        try:
            security_group = db.get_by_id(SecurityGroup, id)
        except NotFoundException as e:
            raise e
        return security_group

    @classmethod
    def update(cls, secgroup_args, id):
        db = DatabaseManager()
        try:
            updated_secgroup = db.get_by_id(SecurityGroup, id)
        except NotFoundException as e:
            raise e
        _sec_rules = secgroup_args.get('rules')
        _new_sec_rules = []
        for _sec_rule_args in _sec_rules:
            _new_sec_rule = Rule(**_sec_rule_args)
            _new_sec_rules.append(_new_sec_rule)
        updated_secgroup.rules = _new_sec_rules or updated_secgroup.rules
        updated_secgroup.name = secgroup_args.get('name') or updated_secgroup.name
        check(security_group=updated_secgroup)
        db.update(updated_secgroup)
        return updated_secgroup

    @classmethod
    def delete(cls, id):
        db = DatabaseManager()
        try:
            security_group_to_remove = db.get_by_id(SecurityGroup, id)
        except NotFoundException as e:
            raise e
        db.remove(security_group_to_remove)
        return security_group_to_remove

    @classmethod
    def get_all(cls):
        db = DatabaseManager()
        return db.get_all(SecurityGroup)

    @classmethod
    def delete_rule(cls, id):
        db = DatabaseManager()
        try:
            db.remove(db.get_by_id(Rule,id))
        except NotFoundException as e:
            raise e