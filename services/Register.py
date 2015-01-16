from services.DatabaseManager import DatabaseManager

__author__ = 'lto'


class Register:

    def __init__(self):
        self.db = DatabaseManager()

    def register_unit(self, unit, ws):
        unit.ws = ws
        unit.state = 'STARTED'
        self.db.update(unit)
