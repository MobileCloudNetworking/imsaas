# Copyright 2014 Technische Universitaet Berlin
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
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
