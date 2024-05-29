# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# NetworkDeviceFunctionsMetrics API File

"""
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
from .network_adapters_api import BNAME as SUB_RESOURCE_BNAME 
from .network_device_functions_api import BNAME as SECONDARY_SUB_RESOURCE_NAME
from .network_adapters_api import members as network_adapters_members

members = {}
BNAME = 'Metrics'


# NetworkDeviceFunctionsMetrics Singleton API
class NetworkDeviceFunctionsMetricsAPI(Resource):

    # kwargs is used to pass in the wildcards values to be replaced
    # when an instance is created via get_<resource>_instance().
    #
    # The call to attach the API establishes the contents of kwargs.
    # All subsequent HTTP calls go through __init__.
    #
    # __init__ stores kwargs in wildcards, which is used to pass
    # values to the get_<resource>_instance() call.
    def __init__(self, **kwargs):
        logging.info('NetworkDeviceFunctionsMetricsAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

    # HTTP GET
    def get(self, ident, ident1, ident2):
        logging.info('NetworkDeviceFunctionsMetricsAPI GET called')
        try:
            resp = 404
            # define the bucket hierarchy
            bucket_hierarchy = [RESOURCE_BNAME, ident, SUB_RESOURCE_BNAME, ident1, SECONDARY_SUB_RESOURCE_NAME, ident2, BNAME]
            # get value of bucket using defined hierarchy
            passed, output = g.get_value_from_bucket_hierarchy(bucket_hierarchy)
            resp = output, 200 if passed else 404        
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self,ident, ident1 , ident2):
        logging.info('NetworkDeviceFunctionsMetricsAPI PUT called')
        return 'PUT is not a supported command for NetworkDeviceFunctionsMetricsAPI', 405

    # HTTP POST
    # This is an emulator-only POST command that creates new resource
    # instances from a predefined template. The new instance is given
    # the identifier "ident", which is taken from the end of the URL.
    # PATCH commands can then be used to update the new instance.
    def post(self, ident, ident1, ident2):
        logging.info('NetworkDeviceFunctionsMetricsAPI POST called')
        try:
            # define the bucket hierarchy
            bucket_hierarchy = [RESOURCE_BNAME, ident, SUB_RESOURCE_BNAME, ident1, SECONDARY_SUB_RESOURCE_NAME, ident2, BNAME]
            # define hierarchy of buckets that should exist before creation of bucket for this resource
            required_buckets_hierarchy = [RESOURCE_BNAME, ident, SUB_RESOURCE_BNAME, ident1, SECONDARY_SUB_RESOURCE_NAME, ident2]
            
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
            resp = request.json, 201

        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PATCH
    def patch(self, ident, ident1):
        logging.info('NetworkDeviceFunctionsMetricsAPI PATCH called')
        raw_dict = request.get_json(force=True)
        try:
            # Update specific portions of the identified object
            for key, value in raw_dict.items():
                members[ident][key] = value
            resp = members[ident], 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP DELETE
    def delete(self, ident, ident1):
        logging.info('NetworkDeviceFunctionsMetricsAPI DELETE called')
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

