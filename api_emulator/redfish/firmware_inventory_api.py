# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# FirmwareInventory API File

"""
Collection API:  GET
Singleton  API:  GET, POST
"""

import g

import sys, traceback, json
import logging
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource

from g import INTERNAL_SERVER_ERROR

INDICES = [0,2]

# FirmwareInventory Singleton API
class FirmwareInventoryAPI(Resource):

    # kwargs is used to pass in the wildcards values to be replaced
    # when an instance is created via get_<resource>_instance().
    #
    # The call to attach the API establishes the contents of kwargs.
    # All subsequent HTTP calls go through __init__.
    #
    # __init__ stores kwargs in wildcards, which is used to pass
    # values to the get_<resource>_instance() call.


    def __init__(self, **kwargs):
        logging.info('FirmwareInventoryAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

    # HTTP GET
    def get(self, ident):
        logging.info('FirmwareInventoryAPI GET called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.get_value_from_bucket_hierarchy(bucket_hierarchy, INDICES)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self, ident):
        logging.info('FirmwareInventoryAPI PUT called')
        return 'PUT is not a supported command for FirmwareInventoryAPI', 405

    # HTTP POST
    def post(self, ident):
        logging.info('FirmwareInventoryAPI POST called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.post_value_to_bucket_hierarchy(bucket_hierarchy, INDICES, request.json)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PATCH
    def patch(self, ident):
        logging.info('FirmwareInventoryAPI PATCH called')
        return 'PATCH is not a supported command for FirmwareInventoryAPI', 405

    # HTTP DELETE
    def delete(self, ident):
        logging.info('FirmwareInventoryAPI DELETE called')
        return 'DELETE is not a supported command for FirmwareInventoryAPI', 405

# FirmwareInventory Collection API
class FirmwareInventoryCollectionAPI(Resource):

    def __init__(self):
        logging.info('FirmwareInventoryCollectionAPI init called')
        self.rb = g.rest_base
        bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
        passed, output = g.get_collection_from_bucket_hierarchy(bucket_hierarchy, INDICES[:-1])
        if not passed:
            return output, 404
        self.config = {
            '@odata.id': self.rb + 'UpdateService/FirmwareInventory',
            '@odata.type': '#FirmwareInventoryCollection.1.0.0.FirmwareInventoryCollection',
            '@odata.context': self.rb + '$metadata#FirmwareInventoryCollection.FirmwareInventoryCollection',
            'Description': 'Inventory of Firmware components',
            'Name': 'Firmware Inventory',
            'Members': [{'@odata.id': x} for x in output],
            'Members@odata.count': len(output)
        }

    # HTTP GET
    def get(self):
        logging.info('FirmwareInventoryCollectionAPI GET called')
        try:
            resp = self.config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self):
        logging.info('FirmwareInventoryCollectionAPI PUT called')
        return 'PUT is not a supported command for FirmwareInventoryCollectionAPI', 405

    def verify(self, config):
        #TODO: Implement a method to verify that the POST body is valid
        return True,{}

    # HTTP POST
    def post(self):
        logging.info('FirmwareInventoryCollectionAPI POST called')
        return 'POST is not a supported command for FirmwareInventoryCollectionAPI', 405
 
    # HTTP PATCH
    def patch(self):
        logging.info('FirmwareInventoryCollectionAPI PATCH called')
        return 'PATCH is not a supported command for FirmwareInventoryCollectionAPI', 405

    # HTTP DELETE
    def delete(self):
        logging.info('FirmwareInventoryCollectionAPI DELETE called')
        return 'DELETE is not a supported command for FirmwareInventoryCollectionAPI', 405

