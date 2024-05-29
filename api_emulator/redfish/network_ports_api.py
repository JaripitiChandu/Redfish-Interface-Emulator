# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# NetworkPorts API File

"""
Collection API:  GET
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
from .network_adapters_api import BNAME as SUB_RESOURCE_BNAME 

members = {}

INTERNAL_ERROR = 500
BNAME = 'NetworkPorts'

# NetworkPorts Singleton API
class NetworkPortsAPI(Resource):

    # kwargs is used to pass in the wildcards values to be replaced
    # when an instance is created via get_<resource>_instance().
    #
    # The call to attach the API establishes the contents of kwargs.
    # All subsequent HTTP calls go through __init__.
    #
    # __init__ stores kwargs in wildcards, which is used to pass
    # values to the get_<resource>_instance() call.
    def __init__(self, **kwargs):
        logging.info('NetworkPortsAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

    # HTTP GET
    def get(self, ident, ident1, ident2):
        logging.info('NetworkPortsAPI GET called')
        try:
            resp = 404
            # define the bucket hierarchy
            bucket_hierarchy = [RESOURCE_BNAME, ident, SUB_RESOURCE_BNAME, ident1, BNAME, ident2]
            # get value of bucket using defined hierarchy
            passed, output = g.get_value_from_bucket_hierarchy(bucket_hierarchy)
            resp = output, 200 if passed else 404
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self,ident, ident1 , ident2):
        logging.info('NetworkPortsAPI PUT called')
        return 'PUT is not a supported command for NetworkPortsAPI', 405

    # HTTP POST
    def post(self, ident, ident1, ident2):
        logging.info('NetworkPortsAPI POST called')
        try:
            # define the bucket hierarchy
            bucket_hierarchy = [RESOURCE_BNAME, ident, SUB_RESOURCE_BNAME, ident1, BNAME, ident2]
            # define hierarchy of buckets that should exist before creation of bucket for this resource
            required_buckets_hierarchy = [RESOURCE_BNAME, ident, SUB_RESOURCE_BNAME, ident1]            
            
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
    def patch(self, ident, ident1, ident2):
        logging.info('NetworkPortsAPI PATCH called')
        patch_data = request.get_json(force=True)
        logging.info(f"Payload = {patch_data}")
        try:
            bucket_hierarchy = [RESOURCE_BNAME, ident, SUB_RESOURCE_BNAME, ident1, BNAME, ident2]

            passed, ports_data = g.get_value_from_bucket_hierarchy(bucket_hierarchy)

            if not passed:
                return f"NetworkPort {ident2} of NetworkAdapter {ident1} for Chassis {ident} not found", 404

            for key, value in patch_data.items():
                if key in ports_data:
                    ports_data[key] = value

            g.post_value_to_bucket_hierarchy(bucket_hierarchy, json.dumps(ports_data))
            resp = ports_data, 200

        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP DELETE
    def delete(self, ident, ident1):
        logging.info('NetworkPortsAPI DELETE called')
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


# NetworkPorts Collection API
class NetworkPortsCollectionAPI(Resource):

    def __init__(self):
        logging.info('NetworkPortsCollectionAPI init called')
        self.rb = g.rest_base
        self.config = {
            '@odata.id': " ",
            '@odata.type': '#NetworkPortCollection.NetworkPSortCollection',
            '@odata.context': self.rb + '$metadata#NetworkPortCollection.NetworkPortCollection',
            'Name': 'NetworkPorts Collection',
            "Members": [],
            "Members@odata.count": 0
        }

    # HTTP GET
    def get(self,ident,ident1):
        logging.info('NetworkPortsCollectionAPI GET called')
        try:
            # define the bucket hierarchy for collection
            bucket_hierarchy = [RESOURCE_BNAME, ident, SUB_RESOURCE_BNAME, ident1, BNAME]
            # get list of resources
            passed, output = g.get_collection_from_bucket_hierarchy(bucket_hierarchy)
            if not passed:
                return output, 404
            # update the value of config using obtained values
            self.config["@odata.id"] = "/redfish/v1/Chassis/{}/NetworkAdapters/{}/NetworkPorts".format(ident,ident1)
            self.config["Members"] = [{'@odata.id': x} for x in output]
            self.config["Members@odata.count"] = len(output)
            resp = self.config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self,ident):
        logging.info('NetworkPortsCollectionAPI PUT called')
        return 'PUT is not a supported command for NetworkPortsCollectionAPI', 405

    def verify(self, config):
        #TODO: Implement a method to verify that the POST body is valid
        return True,{}

    # HTTP POST
    def post(self,ident):
        logging.info('NetworkPortsCollectionAPI POST called')
        return 'POST is not a supported command for NetworkPortsCollectionAPI', 405

    # HTTP PATCH
    def patch(self):
        logging.info('NetworkPortsCollectionAPI PATCH called')
        return 'PATCH is not a supported command for NetworkPortsCollectionAPI', 405

    # HTTP DELETE
    def delete(self):
        logging.info('NetworkPortsCollectionAPI DELETE called')
        return 'DELETE is not a supported command for NetworkPortsCollectionAPI', 405
