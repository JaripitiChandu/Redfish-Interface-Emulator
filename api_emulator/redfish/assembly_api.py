# Copyright Notice:
# Copyright 2016-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# Thermal API File

"""
Collection API:  (None)
Singleton  API:  GET, POST
"""

import g
from g import INTERNAL_SERVER_ERROR as INTERNAL_ERROR

import json
import sys, traceback
import logging
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource

from .Chassis_api import BNAME as RESOURCE_BNAME

members = {}
BNAME = 'Assembly'
INDICES = [1,2]


# Thermal API
class AssemblyAPI(Resource):

    # kwargs is used to pass in the wildcards values to be replaced
    # when an instance is created via get_<resource>_instance().
    #
    # The call to attach the API establishes the contents of kwargs.
    # All subsequent HTTP calls go through __init__.
    #
    # __init__ stores kwargs in wildcards, which is used to pass
    # values to the get_<resource>_instance() call.

    temp_schema = {
        "title": "temperature",
        "type": "object",
        "properties": {
            "ReadingCelcius": {
                "type": "integer",
                "minimum": 4,
                "maximum": 50
            },
            "UpperThresholdNonCritical": {
                "type": "integer",
                "minimum": 4,
                "maximum": 50
            },
            "UpperThresholdCritical": {
                "type": "integer",
                "minimum": 4,
                "maximum": 50
            },
            "UpperThresholdFatal": {
                "type": "integer",
                "minimum": 4,
                "maximum": 50
            },
            "LowerThresholdNonCritical": {
                "type": "integer",
                "minimum": 4,
                "maximum": 50
            },
            "LowerThresholdCritical": {
                "type": "integer",
                "minimum": 4,
                "maximum": 50
            },
            "LowerThresholdFatal": {
                "type": "integer",
                "minimum": 4,
                "maximum": 50
            },
        },
    }

    def __init__(self, **kwargs):
        logging.info('AssemblyAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

    # HTTP GET
    def get(self, ident):
        logging.info('AssemblyAPI GET called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.get_value_from_bucket_hierarchy(bucket_hierarchy, INDICES)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    @g.delay_response()
    def put(self,ident):
        logging.info('CreateAssembly put called')
        try:
            global wildcards
            wildcards['ch_id'] = ident
            logging.info(wildcards)
            config=get_thermal_instance(wildcards)
            members[ident]=config
            resp = config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp
    # def put(self, ident):
    #     logging.info('ThermalAPI PUT called')
    #     return 'PUT is not a supported command for ThermalAPI', 405

    # HTTP POST
    def post(self, ident):
        logging.info('AssemblyAPI POST called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.post_value_to_bucket_hierarchy(bucket_hierarchy, INDICES, request.json)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PATCH
    # @g.delay_response()
    # @g.validate_json(temp_schema)
    def patch(self, ident):
        logging.info(self.__class__.__name__ + ' PATCH called')
        patch_data = request.get_json(force=True)
        logging.info(f"Payload = {patch_data}")
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.patch_bucket_value(bucket_hierarchy, INDICES, patch_data)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP DELETE
    def delete(self, ident):
        logging.info('ThermalAPI DELETE called')
        return 'DELETE is not a supported command for ThermalAPI', 405


# ThermalCollection API
# Thermal does not have a collection API
