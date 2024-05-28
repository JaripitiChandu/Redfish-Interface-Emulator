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

from g import INDEX, INTERNAL_SERVER_ERROR

PRIMARY_BNAME = b'UpdateService'
BNAME = b'FirmwareInventory'

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
            with g.db.view() as tx:
                b = tx.bucket(PRIMARY_BNAME).bucket(BNAME)
                if not b:
                    resp = f"FirmwareInventory for UpdateService not found"
                else:
                    ident_bucket = b.bucket(str(ident).encode())
                    if not ident_bucket:
                        resp = f" {ident} for FirmwareInventory in UpdateService not found", 404
                    else:
                        value = ident_bucket.get(INDEX).decode()
                        resp = json.loads(value), 200
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
            resp = 404
            with g.db.update() as tx:
                updateservice = tx.bucket(PRIMARY_BNAME)
                if updateservice:
                    firmware_inv = updateservice.bucket(BNAME)
                else:
                    return f"UpdateService not found"

                if not firmware_inv:
                    firmware_inv = updateservice.create_bucket(BNAME)
                
                if firmware_inv.bucket(str(ident).encode()):
                    return f"{ident} of FirmwareInventory in UpdateService already exists"
                else:
                    firmware_inv_ident = firmware_inv.create_bucket(str(ident).encode())
                    firmware_inv_ident.put(INDEX, json.dumps(request.json).encode())
                    resp = request.json, 201      
            
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
        bucket_members = []

        with g.db.view() as tx:
            b = tx.bucket(PRIMARY_BNAME).bucket(BNAME)
            if not b:
                    resp = f'FirmwareInventory of UpdateService not found', 404
            else:
                for k, v in b:
                    if not v:
                        if b.bucket(k):
                            bucket_members.append(json.loads(b.bucket(k).get(INDEX).decode())['@odata.id'])
        self.config = {
            '@odata.id': self.rb + 'UpdateService/FirmwareInventory',
            '@odata.type': '#FirmwareInventoryCollection.1.0.0.FirmwareInventoryCollection',
            '@odata.context': self.rb + '$metadata#FirmwareInventoryCollection.FirmwareInventoryCollection',
            'Name': 'FirmwareInventory Collection',
            'Members': [{'@odata.id': x} for x in bucket_members],
            'Members@odata.count': len(bucket_members)
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

