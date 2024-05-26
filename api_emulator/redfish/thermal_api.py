# Copyright Notice:
# Copyright 2016-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# Thermal API File

"""
Collection API:  (None)
Singleton  API:  GET, POST
"""

import g
from g import INDEX, db

import json
import sys, traceback
import logging
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource

from .Chassis_api import BNAME as RESOURCE_BNAME

members = {}

BNAME = 'Thermal'
INTERNAL_ERROR = 500


# Thermal API
class ThermalAPI(Resource):

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
        logging.info('ThermalAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

    # HTTP GET
    def get(self, ident):
        logging.info('ThermalAPI GET called')
        try:
            resp = 404
            # define the bucket hierarchy
            bucket_hierarchy = [RESOURCE_BNAME, ident, BNAME]
            # get value of bucket using defined hierarchy
            passed, output = g.get_value_from_bucket_hierarchy(bucket_hierarchy)
            resp = output, 200 if passed else 404    
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    @g.delay_response()
    def put(self,ident):
        logging.info('CreateThermal put called')
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
        logging.info('ThermalAPI POST called')
        try:
            # define the bucket hierarchy
            bucket_hierarchy = [RESOURCE_BNAME, ident, BNAME]
            # define hierarchy of buckets that should exist before creation of bucket for this resource
            required_buckets_hierarchy = [RESOURCE_BNAME, ident]            
            
            # check if required buckets are present
            passed, message = g.is_required_bucket_hierarchy_present(required_buckets_hierarchy)
            if not passed:
                return message, 404
            
            # check if bucket already exists for current resource
            passed, message = g.is_not_resource_bucket_already_present_in_hierarchy(bucket_hierarchy)
            if not passed:
                return message, 409
            
            # now create the required bucket for resource and put value
            g.post_value_to_bucket_hierarchy(bucket_hierarchy, json.dumps(request.json))
            resp = request.json, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PATCH
    # @g.delay_response()
    # @g.validate_json(temp_schema)
    def patch(self, ident):
        logging.info('ThermalAPI PATCH called')
        raw_dict = request.get_json(force=True)
        logging.info(raw_dict)
        try:
            # Update specific portions of the identified object
            logging.info(members[ident])
            for key, value in raw_dict.items():
                logging.info('Update ' + key + ' to ' + str(value))
                members[ident][key] = value
            logging.info(members[ident])
            resp = members[ident], 200
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
