# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# LogService API File

"""
Collection API:  GET
Singleton  API:  GET, POST
"""

import g

import sys, traceback
import logging, json
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource

from g import INDEX, INTERNAL_SERVER_ERROR

members = {}

PRIMARY_BNAME = b'Managers'
BNAME = b'LogServices'

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
                            resp = f"{BNAME.decode('utf-8')} {ident1} for Manager {ident} not found", 404
                        else:
                            value = ident_bucket.get(INDEX).decode()
                            resp = json.loads(value), 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self,ident, ident1):
        logging.info('LogServiceAPI PUT called')
        return 'PUT is not a supported command for LogServiceAPI', 405

    # HTTP POST
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
                    return f"Manager {ident} not found", 404

                if not log_services:
                    log_services=managers_ident.create_bucket(BNAME)

                log_services_index = log_services.bucket(str(ident1).encode())

                if log_services_index:
                    return f"{BNAME.decode('utf-8')} {ident1} already exists in Manager {ident}", 409
                else:
                    ident_bucket = log_services.create_bucket(str(ident1).encode())
                    ident_bucket.put(INDEX, json.dumps(request.json).encode())
                    resp = request.json, 201

        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PATCH
    def patch(self, ident, ident1):
        logging.info('LogServiceAPI PATCH called')
        patch_data = request.get_json(force=True)
        logging.info(f"Payload = {patch_data}")
        try:
            # Update specific portions of the identified object
            with g.db.update() as tx:
                managers = tx.bucket(PRIMARY_BNAME)
                if managers:
                    managers_ident = managers.bucket(str(ident).encode())
                    if managers_ident:
                        log_services = managers_ident.bucket(BNAME)
                        if log_services:
                            log_services_ident = log_services.bucket(str(ident1).encode())
                        else:
                            return f"Logservice {ident1} for Manager {ident} not found", 404
                    else:
                        return f"Manager {ident} not found", 404
                else:
                    return f"Manager {ident} not found", 404

                if log_services_ident:
                    log_service_data = json.loads(log_services_ident.get(INDEX).decode())
                else:
                    return f"Logservice {ident1} for Manager {ident} not found", 404

                for key, value in patch_data.items():
                    if key in log_service_data:
                        log_service_data[key] = value

                    log_services_ident.put(INDEX, json.dumps(log_service_data).encode())
                    resp = log_service_data, 200

        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP DELETE
    def delete(self, ident, ident1):
        logging.info('LogServiceAPI DELETE called')
        return 'DELETE is not a supported command for LogServiceAPI', 405

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
            resp = INTERNAL_SERVER_ERROR
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


