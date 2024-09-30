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

BNAME = b"CertificateLocations"
INDICES = [0,1]

INTERNAL_ERROR = 500


# AccountService Resource API
class CertificateLocationsAPI(Resource):

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
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.get_value_from_bucket_hierarchy(bucket_hierarchy, INDICES)
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
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.post_value_to_bucket_hierarchy(bucket_hierarchy, INDICES, request.json)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PATCH    
    def patch(self):
        logging.info(self.__class__.__name__ + ' PATCH called')
        patch_data = request.get_json(force=True)
        logging.info(f"Payload = {patch_data}")
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.patch_bucket_value(bucket_hierarchy, INDICES, patch_data)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP DELETE
    def delete(self):
        logging.info(self.__class__.__name__ + ' DELETE called')
        return f'DELETE is not a supported command for {self.__class__.__name__}', 405


