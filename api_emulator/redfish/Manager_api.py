# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# Manager API File

"""
Collection API:  GET
Singleton  API:  GET, POST
"""

import g
from api_emulator.utils import update_nested_dict

import sys, traceback
import logging, json
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource

# Resource and SubResource imports
from .templates.Manager import get_Manager_instance

from g import db, INDEX, INTERNAL_SERVER_ERROR

BNAME = b'Managers'

# Manager Singleton API
class ManagerAPI(Resource):

    # kwargs is used to pass in the wildcards values to be replaced
    # when an instance is created via get_<resource>_instance().
    #
    # The call to attach the API establishes the contents of kwargs.
    # All subsequent HTTP calls go through __init__.
    #
    # __init__ stores kwargs in wildcards, which is used to pass
    # values to the get_<resource>_instance() call.
    def __init__(self, **kwargs):
        logging.info('ManagerAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

    # HTTP GET
    def get(self, ident):
        logging.info('ManagerAPI GET called')
        try:
            # Find the entry with the correct value for Id
            resp = 404
            with g.db.view() as tx:
                b = tx.bucket(BNAME)
                if b:
                    ident_bucket = b.bucket(str(ident).encode())
                    if not ident_bucket:
                        resp = f"Manager {ident} not found", 404
                    else:
                        value = ident_bucket.get(INDEX).decode()
                        resp = json.loads(value), 200
                else:
                    resp = f"Manager {ident} not found", 404
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self, ident):
        logging.info('ManagerAPI PUT called')
        return 'PUT is not a supported command for ManagerAPI', 405

    # HTTP POST
    def post(self, ident):
        logging.info('ManagerAPI POST called')
        try:
            with g.db.update() as tx:
                b = tx.bucket(BNAME)
                if not b:
                    b = tx.create_bucket(BNAME)
                if b.bucket(str(ident).encode()):
                    resp = f"Manager {ident} already exists", 409
                else:
                    ident_bucket = b.create_bucket(str(ident).encode())
                    ident_bucket.put(INDEX, json.dumps(request.json).encode())
                    resp = request.json, 201
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PATCH
    def patch(self, ident):
        logging.info('ManagerAPI PATCH called')
        raw_dict = request.get_json(force=True)
        logging.info(f"payload = {raw_dict}")
        try:
            with db.update() as tx:
                b = tx.bucket(BNAME)
                if b:
                    mb = b.bucket(str(ident).encode())
                    if mb:
                        config = json.loads(mb.get(INDEX).decode())
                        update_nested_dict(config, raw_dict)
                        mb.put(INDEX, json.dumps(config).encode())
                    else:
                        return f"Manager {ident} not found", 404
                else:
                    return f"Manager {ident} not found", 404
            resp = config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP DELETE
    def delete(self, ident):
        logging.info('ManagerAPI DELETE called')
        return 'DELETE is not a supported command for ManagerAPI', 405


# Manager Collection API
class ManagerCollectionAPI(Resource):

    def __init__(self):
        logging.info('ManagerCollectionAPI init called')
        self.rb = g.rest_base
        bucket_members = []

        with g.db.view() as tx:
            b = tx.bucket(BNAME)
            if not b:
                  resp = f'Manager not found', 404
            else:
                for k, v in b:
                    if not v:
                        if b.bucket(k):
                            bucket_members.append(json.loads(b.bucket(k).get(INDEX).decode())['@odata.id'])
        self.config = {
            '@odata.context': self.rb + '$metadata#ManagerCollection.ManagerCollection',
            '@odata.id': self.rb + 'Managers',
            '@odata.type': '#ManagerCollection.ManagerCollection',
            'Name': 'Manager Collection',
            'Members': [{'@odata.id': x} for x in bucket_members],
            'Members@odata.count': len(bucket_members)
        }

    # HTTP GET
    def get(self):
        logging.info('ManagerCollectionAPI GET called')
        try:
            resp = self.config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self):
        logging.info('ManagerCollectionAPI PUT called')
        return 'PUT is not a supported command for ManagerCollectionAPI', 405

    def verify(self, config):
        #TODO: Implement a method to verify that the POST body is valid
        return True,{}

    # HTTP POST
    # POST should allow adding multiple instances to a collection.
    # For now, this only adds one instance.
    # TODO: 'id' should be obtained from the request data.
    def post(self):
        logging.info('ManagerCollectionAPI POST called')
        return 'POST is not a supported command for ManagerCollectionAPI', 405


    # HTTP PATCH
    def patch(self):
        logging.info('ManagerCollectionAPI PATCH called')
        return 'PATCH is not a supported command for ManagerCollectionAPI', 405

    # HTTP DELETE
    def delete(self):
        logging.info('ManagerCollectionAPI DELETE called')
        return 'DELETE is not a supported command for ManagerCollectionAPI', 405
