# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# NetworkProtocol API File

"""
Singleton  API:  GET, POST
"""

import g

import sys, traceback
import logging , json
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource
from .Manager_api import BNAME as PRIMARY_BNAME
from api_emulator.utils import update_nested_dict

from g import db, INDEX, INTERNAL_SERVER_ERROR

BNAME = b'NetworkProtocols'

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
                    manager_ident = tx.bucket(PRIMARY_BNAME).bucket(str(ident).encode())
                    if manager_ident:
                        network_protocols = manager_ident.bucket(BNAME)
                        if not network_protocols:
                            resp = f"Manager {ident} NetworkProtocols not found", 404
                        else:
                            value = network_protocols.get(INDEX)
                            resp = json.loads(value), 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self,ident, ident1):
        logging.info('NetworkProtocolAPI PUT called')
        return 'PUT is not a supported command for NetworkProtocolAPI', 405

    # HTTP POST
    def post(self, ident):
        logging.info('NetworkProtocolAPI POST called')
        try:
            resp = 404
            with g.db.update() as tx:
                managers = tx.bucket(PRIMARY_BNAME)
                if managers:
                    managers_ident = managers.bucket(str(ident).encode())
                    if managers_ident:
                        network_protocols = managers_ident.bucket(BNAME)
                    else:
                        return f"Manager {ident} not found", 404
                else:
                    return f"Manager {ident} not found", 404

                if not network_protocols:
                    network_protocols = managers_ident.create_bucket(BNAME)
                    network_protocols.put(INDEX, json.dumps(request.json).encode())
                    resp = request.json, 201
                else:
                    return f"NetworkProtocols already exists in Manager {ident}", 409

        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PATCH
    def patch(self, ident):
        logging.info('NetworkProtocolAPI PATCH called')
        raw_dict = request.get_json(force=True)
        logging.info(f"payload = {raw_dict}")
        try:
            with db.update() as tx:
                b = tx.bucket(PRIMARY_BNAME)
                if b:
                    mb = b.bucket(str(ident).encode())
                    if mb:
                        np = mb.bucket(BNAME)
                        if np:
                            config = json.loads(np.get(INDEX).decode())
                            update_nested_dict(config, raw_dict)
                            np.put(INDEX, json.dumps(config).encode())
                        else:
                            return f"NetworkProtocols for Manager {ident} not found", 404
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
        logging.info('NetworkProtocolAPI DELETE called')
        return 'DELETE is not a supported command for NetworkProtocolAPI', 405


