# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# NetworkAdapters API File

"""
Collection API:  GET, POST
Singleton  API:  GET, POST
"""

import g

import json
import sys, traceback
import logging
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource
from .Chassis_api import members as chassis_members
from api_emulator.utils import update_nested_dict

members = {}
PRIMARY_BNAME = b'chassis'
BNAME = b'network_adapters'
INDEX = b'value'
INTERNAL_ERROR = 500


# NetworkAdapters Singleton API
class NetworkAdaptersAPI(Resource):

    # kwargs is used to pass in the wildcards values to be replaced
    # when an instance is created via get_<resource>_instance().
    #
    # The call to attach the API establishes the contents of kwargs.
    # All subsequent HTTP calls go through __init__.
    #
    # __init__ stores kwargs in wildcards, which is used to pass
    # values to the get_<resource>_instance() call.
    def __init__(self, **kwargs):
        logging.info('NetworkAdaptersAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

    # HTTP GET
    def get(self, ident, ident1):
        logging.info('NetworkAdaptersAPI GET called')
        try:
            # Find the entry with the correct value for Id
            resp = 404
            with g.db.view() as tx:
                if not tx.bucket(PRIMARY_BNAME).bucket(str(ident).encode()):
                    resp = f"chassis {ident} not found", 404
                else:
                    b = tx.bucket(PRIMARY_BNAME).bucket(str(ident).encode()).bucket(BNAME)
                    if b:
                        ident_bucket = b.bucket(str(ident1).encode())
                        if not ident_bucket:
                            resp = f"chassis {ident} network adapter {ident1} not found", 404
                        else:
                            value = ident_bucket.get(INDEX).decode()
                            resp = json.loads(value), 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self,ident, ident1):
        logging.info('NetworkAdaptersAPI PUT called')
        return 'PUT is not a supported command for NetworkAdaptersAPI', 405

    # HTTP POST
    # This is an emulator-only POST command that creates new resource
    # instances from a predefined template. The new instance is given
    # the identifier "ident", which is taken from the end of the URL.
    # PATCH commands can then be used to update the new instance.
    def post(self, ident, ident1):
        logging.info('NetworkAdaptersAPI POST called')
        try:
            with g.db.update() as tx:
                if tx.bucket(PRIMARY_BNAME).bucket(str(ident).encode()).bucket(str(ident1).encode()):
                    resp = f"network adapters {ident1} already exists in chassis {ident}", 409
                else:
                    pb = tx.bucket(PRIMARY_BNAME).bucket(str(ident).encode())
                    if not pb:
                        resp = f"chassis {ident} not found", 404
                    else:
                        b = pb.bucket(BNAME)
                        if not b:
                            b = pb.create_bucket(BNAME)
                        ident_bucket = b.create_bucket(str(ident1).encode())
                        ident_bucket.put(INDEX, json.dumps(request.json).encode())
                        resp = request.json, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PATCH
    def patch(self, ident, ident1):
        logging.info('NetworkAdaptersAPI PATCH called')
        raw_dict = request.get_json(force=True)
        logging.info(f"Payload = {raw_dict}")
        try:
            global config
            if ident in chassis_members:
                members.setdefault(ident, {})
            else:
                resp = f"Chassis {ident} not found", 404

            if ident1 in members[ident]:
                update_nested_dict(members[ident][ident1], raw_dict)
                resp = members[ident][ident1], 200
            else:
                return "NetworkAdapter {} does not exist in Chassis {}".format(ident1,ident), 404
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP DELETE
    def delete(self, ident, ident1):
        logging.info('NetworkAdaptersAPI DELETE called')
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


# NetworkAdapters Collection API
class NetworkAdaptersCollectionAPI(Resource):

    def __init__(self):
        logging.info('NetworkAdaptersCollectionAPI init called')
        self.rb = g.rest_base

        self.config = {
            '@odata.id': " ",
            '@odata.type': '#NetworkAdapterCollection.NetworkAdapterCollection',
            '@odata.context': self.rb + '$metadata#NetworkAdapterCollection.NetworkAdapterCollection',
            'Name': 'NetworkAdapters Collection',
            "Members": [],
            "Members@odata.count": 0
        }

    # HTTP GET
    def get(self,ident):
        logging.info('NetworkAdaptersCollectionAPI GET called')
        try:
            bucket_members = []
            with g.db.view() as tx:
                b = tx.bucket(PRIMARY_BNAME).bucket(str(ident).encode()).bucket(BNAME)

                if not b:
                    resp = f'chassis {ident} network adapters not found', 404
                else:
                    for k, v in b:
                        if not v:
                            if b.bucket(k):
                                bucket_members.append(json.loads(b.bucket(k).get(INDEX).decode())['@odata.id'])

            self.config["@odata.id"] = "/redfish/v1/Chassis/{}/NetworkAdapters".format(ident)
            self.config['Members'] = [{'@odata.id': x} for x in bucket_members]
            self.config["Members@odata.count"] = len(bucket_members)
            resp = self.config, 200
            
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self,ident):
        logging.info('NetworkAdaptersCollectionAPI PUT called')
        return 'PUT is not a supported command for NetworkAdaptersCollectionAPI', 405

    def verify(self, config):
        #TODO: Implement a method to verify that the POST body is valid
        return True,{}

    # HTTP POST
    # POST should allow adding multiple instances to a collection.
    # For now, this only adds one instance.
    # TODO: 'id' should be obtained from the request data.
    def post(self,ident):
        logging.info('NetworkAdaptersCollectionAPI POST called')
        return 'POST is not a supported command for NetworkAdaptersCollectionAPI', 405

    # HTTP PATCH
    def patch(self):
        logging.info('NetworkAdaptersCollectionAPI PATCH called')
        return 'PATCH is not a supported command for NetworkAdaptersCollectionAPI', 405

    # HTTP DELETE
    def delete(self):
        logging.info('NetworkAdaptersCollectionAPI DELETE called')
        return 'DELETE is not a supported command for NetworkAdaptersCollectionAPI', 405


