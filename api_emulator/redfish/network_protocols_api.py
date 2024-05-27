# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# NetworkProtocol API File

"""
Collection API:  GET, POST
Singleton  API:  GET, POST
"""

import g

import sys, traceback
import logging , json
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource
from .Manager_api import members as manager_members
from api_emulator.utils import update_nested_dict

members = {}

PRIMARY_BNAME = b'managers'
BNAME = b'network_protocols'

INTERNAL_ERROR = 500


# NetworkProtocol Singleton API
class NetworkProtocolAPI(Resource):

    # kwargs is used to pass in the wildcards values to be replaced
    # when an instance is created via get_<resource>_instance().
    #
    # The call to attach the API establishes the contents of kwargs.
    # All subsequent HTTP calls go through __init__.
    #
    # __init__ stores kwargs in wildcards, which is used to pass
    # values to the get_<resource>_instance() call.
    def __init__(self, **kwargs):
        logging.info('NetworkProtocolAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

    # HTTP GET
    def get(self, ident):
        logging.info('NetworkProtocolAPI GET called')
        try:
            # Find the entry with the correct value for Id
            with g.db.view() as tx:
                if not tx.bucket(PRIMARY_BNAME).bucket(str(ident).encode()):
                    resp = f"Manager {ident} not found", 404
                else:
                    b = tx.bucket(PRIMARY_BNAME).bucket(str(ident).encode())
                    if b:
                        ident_bucket = b.bucket(BNAME)
                        if not ident_bucket:
                            resp = f"Manager {ident} NetworkProtocols not found", 404
                        else:
                            value = ident_bucket.get(BNAME)
                            resp = json.loads(value), 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self,ident, ident1):
        logging.info('NetworkProtocolAPI PUT called')
        return 'PUT is not a supported command for NetworkProtocolAPI', 405

    # HTTP POST
    # This is an emulator-only POST command that creates new resource
    # instances from a predefined template. The new instance is given
    # the identifier "ident", which is taken from the end of the URL.
    # PATCH commands can then be used to update the new instance.
    def post(self, ident):
        logging.info('NetworkProtocolAPI POST called')
        try:
            with g.db.update() as tx:
                if tx.bucket(PRIMARY_BNAME).bucket(str(ident).encode()).bucket(BNAME):
                    resp = f"NetworkProtocols already exists in Manager {ident}", 409
                else:
                    pb = tx.bucket(PRIMARY_BNAME).bucket(str(ident).encode())
                    if not pb:
                        resp = f"Manager {ident} not found", 404
                    else:
                        b = pb.bucket(BNAME)
                        if not b:
                            b = pb.create_bucket(BNAME)
                        b.put(BNAME, json.dumps(request.json).encode())
                        resp = request.json, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PATCH
    def patch(self, ident):
        logging.info('NetworkProtocolAPI PATCH called')
        raw_dict = request.get_json(force=True)
        logging.info(f"payload = {raw_dict}")
        try:
            # Update specific portions of the identified object
            update_nested_dict(members[ident], raw_dict)
            resp = members[ident], 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP DELETE
    def delete(self, ident):
        logging.info('NetworkProtocolAPI DELETE called')
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

