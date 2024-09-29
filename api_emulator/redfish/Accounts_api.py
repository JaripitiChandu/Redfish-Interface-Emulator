# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# Chassis API File

"""
Collection API:  GET, POST
Singleton  API:  GET, POST, PATCH, DELETE
"""

import g

import sys, traceback, json
import logging
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource
from api_emulator.utils import update_nested_dict

from g import db, INDEX, INTERNAL_SERVER_ERROR
from .AccountService_api import BNAME as AS_BNAME

members = {}
BNAME = b"Accounts"
INDICES = [0,2]

# Chassis Singleton API
class Account(Resource):

    # kwargs is used to pass in the wildcards values to be replaced
    # when an instance is created via get_<resource>_instance().
    #
    # The call to attach the API establishes the contents of kwargs.    
    # All subsequent HTTP calls go through __init__.
    #
    # __init__ stores kwargs in wildcards, which is used to pass
    # values to the get_<resource>_instance() call.

    def __init__(self, **kwargs):
        logging.info(f'{self.__class__.__name__} init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

    # HTTP GET
    def get(self, ident):
        logging.info(self.__class__.__name__ +' GET called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.get_value_from_bucket_hierarchy(bucket_hierarchy, INDICES)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self, ident):
        logging.info(self.__class__.__name__ + ' PUT called')
        return f'PUT is not a supported command for {self.__class__.__name__}', 405

    # HTTP POST
    # This is an emulator-only POST command that creates new resource
    # instances from a predefined template. The new instance is given
    # the identifier "ident", which is taken from the end of the URL.
    # PATCH commands can then be used to update the new instance.
    def post(self, ident):
        logging.info(self.__class__.__name__ + ' POST called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.post_value_to_bucket_hierarchy(bucket_hierarchy, INDICES, request.json)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PATCH
    def patch(self, ident):
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
    def delete(self, ident):
        logging.info(self.__class__.__name__ + ' DELETEs called')
        try:
            # Find the entry with the correct value for Id
            resp = 404
            if ident in members:
                del(members[ident])
                resp = 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp


# Chassis Collection API
class Accounts(Resource):

    def __init__(self):
        logging.info(f'{self.__class__.__name__} init called')
        self.rb = g.rest_base
        self.config = {
            "@odata.id": self.rb + "AccountService/Accounts",
            "@odata.type": "#ManagerAccountCollection.ManagerAccountCollection",
            "@odata.context": self.rb + "$metadata#ManagerAccountCollection.ManagerAccountCollection",
            "Description": "Collection of Accounts",
            "Name": "Account Collection",
            "Members": [],
            "Members@odata.count": 0
        }

    # HTTP GET
    def get(self):
        logging.info(self.__class__.__name__ +' GET called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            passed, output = g.get_collection_from_bucket_hierarchy(bucket_hierarchy, INDICES[:-1])
            if not passed:
                return output, 404

            self.config["Members"] = [{'@odata.id': x} for x in output]
            self.config["Members@odata.count"] = len(output)
            resp = self.config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self):
        logging.info(self.__class__.__name__ + ' PUT called')
        return f'PUT is not a supported command for {self.__class__.__name__}', 405

    def verify(self, config):
        #TODO: Implement a method to verify that the POST body is valid
        return True,{}

    # HTTP POST
    # POST should allow adding multiple instances to a collection.
    # For now, this only adds one instance.
    # TODO: 'id' should be obtained from the request data.
    def post(self):
        logging.info(self.__class__.__name__ + ' POST called')
        try:
            config = request.get_json(force=True)
            logging.info(f"Payload = {config}")
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            if len(INDICES)>1:
                split1, split2 = bucket_hierarchy[:INDICES[-2]+1], bucket_hierarchy[INDICES[-2]+1:]
                present, message = g.is_required_bucket_hierarchy_present(bucket_hierarchy[:INDICES[-2]+1], INDICES[:-1])
            if not present:
                return message, 404
            else:
                split1, split2 = tuple(), bucket_hierarchy

            with db.update() as bucket:
                for bucket_name in split1:
                    bucket = bucket.bucket(str(bucket_name).encode())
                for bucket_name in split2:
                    temp = bucket.bucket(str(bucket_name).encode())
                    if not temp:
                        temp = bucket.create_bucket(str(bucket_name).encode())
                    bucket = temp
            if bucket.get(INDEX):
                return g.rest_base+'/'.join(map(str, bucket_hierarchy)) + ' already exists', 409
            bucket.put(INDEX, json.dumps(request.json).encode())
            return {}, 201
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PATCH
    def patch(self):
        logging.info(self.__class__.__name__ + ' PATCH called')
        return 'PATCH is not a supported command for ChassisCollectionAPI', 405

    # HTTP DELETE
    def delete(self):
        logging.info(self.__class__.__name__ + ' DELETE called')
        return 'DELETE is not a supported command for ChassisCollectionAPI', 405