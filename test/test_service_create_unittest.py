import os
import time

from services.DatabaseManager import DatabaseManager
from model.Entities import Service


__author__ = 'mpa'

import httplib
import json

PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
HOST = 'localhost'

import unittest


class ServiceTest(unittest.TestCase):
    def test_create_service(self):
        db = DatabaseManager()
        if len(db.get_all(Service)) > 0:
            self.fail('The Database must be empty: ' + str())

        connection = httplib.HTTPConnection('%s:8090' % HOST)
        headers = {'Content-type': 'application/json'}

        sent_service = {"service_type": "controller", 'image': "nubomedia-broker", 'flavor': "m1.medium",
                        'size': {'def': 1, 'max': 1, 'min': 1}, 'config': {'hostname': 'ControlServer'}}

        sent_service_json = json.dumps(sent_service)

        connection.request('POST', '/services', sent_service_json, headers)
        resp = connection.getresponse()

        self.assertEqual(resp.status, 200)

        service = db.get_by_service_type(Service, sent_service["service_type"])[0]

        self.assertIsNotNone(service)

        self.assertEqual(service.service_type, sent_service["service_type"])
        self.assertEqual(service.image, sent_service["image"])
        self.assertEqual(service.flavor, sent_service["flavor"])
        self.assertEqual(service.size, sent_service['size'])
        self.assertEqual(service.config, sent_service['config'])

        sent_service['flavor'] = "m1.small"

        sent_service_json = json.dumps(sent_service)

        connection.request('PUT', '/services/' + str(service.id), sent_service_json, headers)
        resp = connection.getresponse()

        self.assertEqual(resp.status, 200)

        service = db.get_by_service_type(Service, sent_service["service_type"])[0]
        self.assertIsNotNone(service)
        self.assertEqual(service.service_type, sent_service["service_type"])
        self.assertEqual(service.image, sent_service["image"])
        self.assertEqual(service.flavor, sent_service["flavor"])
        self.assertEqual(service.size, sent_service['size'])
        self.assertEqual(service.config, sent_service['config'])

        connection.request('DELETE', '/services/' + str(service.id), sent_service_json, headers)

        time.sleep(2)

        self.assertEqual(len(db.get_by_service_type(Service, sent_service["service_type"])), 0)


if __name__ == '__main__':
    unittest.main()