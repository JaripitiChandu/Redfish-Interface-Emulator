# Copyright Notice:
# Copyright 2016-2021 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# AccountService API File

"""
Collection API:  GET
Singleton  API:  (None)
"""

import g

import sys, traceback, json
import logging
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Resource
from api_emulator.utils import update_nested_dict

from g import db, INDEX, INTERNAL_SERVER_ERROR

BNAME = b"AccountService"

INTERNAL_ERROR = 500


# AccountService Resource API
class AccountServiceAPI(Resource):

    def __init__(self, **kwargs):
        logging.info(f'{self.__class__.__name__} init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()       

    # HTTP GET
    def get(self):
        logging.info(self.__class__.__name__ +' GET called')
        try:
            # Find the entry with the correct value for Id
            with db.view() as tx:
                b = tx.bucket(BNAME)
                if not b:
                    return "AccountService not found" , 404
                else:
                    resp = json.loads(b.get(INDEX).decode()), 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self):
        logging.info(self.__class__.__name__ + ' PUT called')
        return f'PUT is not a supported command for {self.__class__.__name__}', 405

    # HTTP POST
    def post(self):
        logging.info(self.__class__.__name__ + ' POST called')
        try:
            with db.update() as tx:
                b = tx.bucket(BNAME)
                if b:
                    resp = "AccountService already present", 409
                else:
                    b = tx.create_bucket(BNAME)
                    b.put(INDEX, json.dumps(request.json).encode())
            resp = request.json, 201
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PATCH    
    def patch(self):
        logging.info(self.__class__.__name__ + ' PATCH called')
        raw_dict = request.get_json(force=True)
        logging.info(f"payload = {json.dumps(raw_dict)}")
        try:
            with db.update() as tx:
                b = tx.bucket(BNAME)
                if b:
                    config = json.loads(b.get(INDEX).decode())
                    update_nested_dict(config, raw_dict)
                    b.put(INDEX, json.dumps(config).encode())
                else:
                    return f"AccountService not found", 404
            resp = config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP DELETE
    def delete(self):
        logging.info(self.__class__.__name__ + ' DELETE called')
        return f'DELETE is not a supported command for {self.__class__.__name__}', 405


