# Copyright Notice:
# Copyright 2016-2021 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# UpdateService API File

"""
Collection API:  GET
Singleton  API:  (None)
"""

import g

import sys, traceback
import logging
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource

config = {}

INTERNAL_ERROR = 500


# UpdateService Singleton API
# UpdateService does not have a Singleton API


# UpdateService Collection API
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
            global config
            resp = config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self):
        logging.info('UpdateServiceAPI PUT called')
        return 'PUT is not a supported command for UpdateServiceAPI', 405

    # HTTP POST
    def post(self):
        logging.info('UpdateServiceAPI POST called')
        try:
            global config
            config=request.json
            resp = config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PATCH
    def patch(self):
        logging.info('UpdateServiceAPI PATCH called')
        return 'PATCH is not a supported command for UpdateServiceAPI', 405

    # HTTP DELETE
    def delete(self):
        logging.info('UpdateServiceAPI DELETE called')
        return 'DELETE is not a supported command for UpdateServiceAPI', 405


