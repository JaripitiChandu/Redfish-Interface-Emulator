# Copyright Notice:
# Copyright 2016-2021 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# UpdateService API File

"""
Singleton  API: GET, POST
"""

import g

import sys, traceback
import logging,json
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource

from g import INDEX, INTERNAL_SERVER_ERROR

PRIMARY_BNAME=b'UpdateService'

# UpdateService Singleton API
class UpdateServiceAPI(Resource):

    def __init__(self, **kwargs):
        logging.info('UpdateServiceAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()       

    # HTTP GET
    def get(self):
        logging.info('UpdateServiceAPI GET called')
        try:
            resp = 404
            with g.db.view() as tx:
                b = tx.bucket(PRIMARY_BNAME)                    
                if not b:
                    resp = f"UpdateService not found", 404
                else:
                    value = b.get(INDEX).decode()
                    resp = json.loads(value), 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self):
        logging.info('UpdateServiceAPI PUT called')
        return 'PUT is not a supported command for UpdateServiceAPI', 405

    # HTTP POST
    def post(self):
        logging.info('UpdateServiceAPI POST called')
        try:
            resp = 404
            with g.db.update() as tx:
                updateservice = tx.bucket(PRIMARY_BNAME)
                if updateservice:
                    resp = f"UpdateService already exists", 404
                else:
                    updateservice = tx.create_bucket(PRIMARY_BNAME)
                    updateservice.put(INDEX, json.dumps(request.json).encode())
                    resp = request.json, 201
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PATCH
    def patch(self):
        logging.info('UpdateServiceAPI PATCH called')
        return 'PATCH is not a supported command for UpdateServiceAPI', 405

    # HTTP DELETE
    def delete(self):
        logging.info('UpdateServiceAPI DELETE called')
        return 'DELETE is not a supported command for UpdateServiceAPI', 405


