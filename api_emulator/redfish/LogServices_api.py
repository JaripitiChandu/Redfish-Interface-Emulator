# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# LogService API File

"""
Collection API:  GET, POST
Singleton  API:  GET, POST
"""

import g

import sys, traceback
import logging, json
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource
from .Manager_api import members as manager_members
from api_emulator.utils import update_nested_dict

members = {}

PRIMARY_BNAME = b'managers'
BNAME = b'log_services'
INDEX = b'value'

INTERNAL_ERROR = 500


# LogService Singleton API
class LogServiceAPI(Resource):

    # kwargs is used to pass in the wildcards values to be replaced
    # when an instance is created via get_<resource>_instance().
    #
    # The call to attach the API establishes the contents of kwargs.
    # All subsequent HTTP calls go through __init__.
    #
    # __init__ stores kwargs in wildcards, which is used to pass
    # values to the get_<resource>_instance() call.
    def __init__(self, **kwargs):
        logging.info('LogServiceAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

    # HTTP GET
    def get(self, ident, ident1):
        logging.info('LogServiceAPI GET called')
        try:
            # Find the entry with the correct value for Id
            resp = 404
            with g.db.view() as tx:
                if not tx.bucket(PRIMARY_BNAME).bucket(str(ident).encode()):
                    resp = f"Manager {ident} not found", 404
                else:
                    b = tx.bucket(PRIMARY_BNAME).bucket(str(ident).encode()).bucket(BNAME)
                    if b:
                        ident_bucket = b.bucket(str(ident1).encode())
                        if not ident_bucket:
                            resp = f"LogService {ident1} for Manager {ident} not found", 404
                        else:
                            value = ident_bucket.get(INDEX).decode()
                            resp = json.loads(value), 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self,ident, ident1):
        logging.info('LogServiceAPI PUT called')
        return 'PUT is not a supported command for LogServiceAPI', 405

    # HTTP POST
    # This is an emulator-only POST command that creates new resource
    # instances from a predefined template. The new instance is given
    # the identifier "ident", which is taken from the end of the URL.
    # PATCH commands can then be used to update the new instance.
    def post(self, ident, ident1):
        logging.info('LogServiceAPI POST called')
        try:
            with g.db.update() as tx:
                managers = tx.bucket(PRIMARY_BNAME)
                if managers:
                    managers_ident = managers.bucket(str(ident).encode())
                    if managers_ident:
                        log_services=managers_ident.bucket(BNAME)
                else:
                    resp = f"Manager {ident} not found", 404

                if not log_services:
                    log_services=managers_ident.create_bucket(BNAME)

                log_services_index = log_services.bucket(str(ident1).encode())

                if log_services_index:
                    resp = f"LogService {str(ident1).encode()} already exists in Manager {ident}", 409
                else:
                    ident_bucket = log_services.create_bucket(str(ident1).encode())
                    ident_bucket.put(INDEX, json.dumps(request.json).encode())
                    resp = request.json, 200

        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PATCH
    def patch(self, ident, ident1):
        logging.info('LogServiceAPI PATCH called')
        raw_dict = request.get_json(force=True)
        logging.info(f"Payload = {raw_dict}")
        try:
            global config
            if ident in manager_members:
                members.setdefault(ident, {})
                members[ident][ident1] = request.json
            else:
                resp = f"Manager {ident} not found", 404
            
            update_nested_dict(members[ident][ident1], raw_dict)
            resp = members[ident][ident1], 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP DELETE
    def delete(self, ident, ident1):
        logging.info('LogServiceAPI DELETE called')
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


# LogService Collection API
class LogServiceCollectionAPI(Resource):

    def __init__(self):
        logging.info('LogServiceCollectionAPI init called')
        self.rb = g.rest_base
        self.config = {
            '@odata.id': " ",
            '@odata.type': '#LogServiceCollection.LogServiceCollection',
            '@odata.context': self.rb + '$metadata#LogServiceCollection.LogServiceCollection',
            'Name': 'Ethernet Interfaces Collection',
            "Members": [],
            "Members@odata.count": 0,
            "Description": "Collection of LogServices for this Manager"
        }

    # HTTP GET
    def get(self,ident):
        logging.info('LogServiceCollectionAPI GET called')
        try:
            bucket_members = []
            with g.db.view() as tx:
                b = tx.bucket(PRIMARY_BNAME).bucket(str(ident).encode()).bucket(BNAME)

                if not b:
                    resp = f'Managers {ident} CiscoInternalStorage not found', 404
                else:
                    for k, v in b:
                        if not v:
                            if b.bucket(k):
                                bucket_members.append(json.loads(b.bucket(k).get(INDEX).decode())['@odata.id'])
            self.config["@odata.id"] = "/redfish/v1/Manager/{}/LogServices".format(ident)
            self.config['Members'] = [{'@odata.id': x} for x in bucket_members]
            self.config["Members@odata.count"] = len(bucket_members)
            resp = self.config, 200
            
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self,ident):
        logging.info('LogServiceCollectionAPI PUT called')
        return 'PUT is not a supported command for LogServiceCollectionAPI', 405

    def verify(self, config):
        #TODO: Implement a method to verify that the POST body is valid
        return True,{}

    # HTTP POST
    # POST should allow adding multiple instances to a collection.
    # For now, this only adds one instance.
    # TODO: 'id' should be obtained from the request data.
    def post(self,ident):
        logging.info('LogServiceCollectionAPI POST called')
        return 'POST is not a supported command for LogServiceCollectionAPI', 405

    # HTTP PATCH
    def patch(self):
        logging.info('LogServiceCollectionAPI PATCH called')
        return 'PATCH is not a supported command for LogServiceCollectionAPI', 405

    # HTTP DELETE
    def delete(self):
        logging.info('LogServiceCollectionAPI DELETE called')
        return 'DELETE is not a supported command for LogServiceCollectionAPI', 405


