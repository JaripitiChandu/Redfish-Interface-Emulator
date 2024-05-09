# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# FirmwareInventory API File

"""
Collection API:  GET
Singleton  API:  GET, POST, PATCH, DELETE
"""

import g

import sys, traceback, json
import logging
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource

members = {}

INTERNAL_ERROR = 500

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
            # Find the entry with the correct value for Id
            resp = 404
            if ident in members:
                resp = members[ident], 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self, ident):
        logging.info('FirmwareInventoryAPI PUT called')
        return 'PUT is not a supported command for FirmwareInventoryAPI', 405

    # HTTP POST
    # This is an emulator-only POST command that creates new resource
    # instances from a predefined template. The new instance is given
    # the identifier "ident", which is taken from the end of the URL.
    # PATCH commands can then be used to update the new instance.
    def post(self, ident):
        logging.info('FirmwareInventoryAPI POST called')
        try:
            global config
            config=request.json
            members[ident]=config
            resp = config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP DELETE
    def delete(self, ident):
        logging.info('FirmwareInventoryAPI DELETE called')
        try:
            # Find the entry with the correct value for Id
            resp = 404
            if ident in members:
                del(members[ident])
                resp = 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp


# FirmwareInventory Collection API
class FirmwareInventoryCollectionAPI(Resource):

    def __init__(self):
        logging.info('FirmwareInventoryCollectionAPI init called')
        self.rb = g.rest_base
        self.config = {
            '@odata.id': self.rb + 'UpdateService/FirmwareInventory',
            '@odata.type': '#FirmwareInventoryCollection.1.0.0.FirmwareInventoryCollection',
            '@odata.context': self.rb + '$metadata#FirmwareInventoryCollection.FirmwareInventoryCollection',
            'Name': 'FirmwareInventory Collection',
            'Members': [{'@odata.id': x['@odata.id']} for
                        x in list(members.values())],
            'Members@odata.count': len(members)
        }

    # HTTP GET
    def get(self):
        logging.info('FirmwareInventoryCollectionAPI GET called')
        try:
            resp = self.config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
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

