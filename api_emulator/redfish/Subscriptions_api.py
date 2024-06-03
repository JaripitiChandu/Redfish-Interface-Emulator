# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# Subscriptions API File

"""
Collection API:  GET, POST
Singleton  API:  GET, POST, PATCH, DELETE
"""

import g

import sys, traceback
import logging, json
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource

# Resource and SubResource imports
from .templates.Subscription import get_Subscription_instance

from g import INTERNAL_SERVER_ERROR

INDICES = [0,2]

# Subscription Singleton API
class SubscriptionAPI(Resource):

    # kwargs is used to pass in the wildcards values to be replaced
    # when an instance is created via get_<resource>_instance().
    #
    # The call to attach the API establishes the contents of kwargs.
    # All subsequent HTTP calls go through __init__.
    #
    # __init__ stores kwargs in wildcards, which is used to pass
    # values to the get_<resource>_instance() call.
    def __init__(self, **kwargs):
        logging.info('SubscriptionAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

    # HTTP GET
    def get(self, ident):
        logging.info('SubscriptionAPI GET called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.get_value_from_bucket_hierarchy(bucket_hierarchy, INDICES)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self, ident):
        logging.info('SubscriptionAPI PUT called')
        return 'PUT is not a supported command for SubscriptionAPI', 405

    # HTTP POST
    def post(self, ident):
        logging.info('SubscriptionAPI POST called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.post_value_to_bucket_hierarchy(bucket_hierarchy, INDICES, request.json)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        logging.info('SubscriptionAPI POST exit')
        return resp

    # HTTP PATCH
    def patch(self, ident):
        logging.info('SubscriptionAPI PATCH called')
        return 'PATCH is not a supported command for SubscriptionAPI', 405

    # HTTP DELETE
    def delete(self, ident):
        logging.info('SubscriptionAPI DELETE called')
        return 'DELETE is not a supported command for SubscriptionAPI', 405

# Subscription Collection API
class SubscriptionCollectionAPI(Resource):

    def __init__(self):
        logging.info('SubscriptionCollectionAPI init called')
        self.rb = g.rest_base
        self.config = {
            "@odata.id": "/redfish/v1/EventService/Subscriptions",
            "@odata.type": "#EventDestinationCollection.EventDestinationCollection",
            "@odata.context": "/redfish/v1/$metadata#EventDestinationCollection.EventDestinationCollection",
            "Description": "List of Event subscriptions",
            "Name": "Event Subscriptions Collection",
            "Members": [],
            "Members@odata.count": 0
        }

    # HTTP GET
    def get(self):
        logging.info('SubscriptionCollectionAPI GET called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            passed, output = g.get_collection_from_bucket_hierarchy(bucket_hierarchy, INDICES[:-1])
            if not passed:
                return output, 404
            self.config['Members'] = [{'@odata.id': x} for x in output]
            self.config["Members@odata.count"] = len(output)
            resp = self.config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self):
        logging.info('SubscriptionCollectionAPI PUT called')
        return 'PUT is not a supported command for SubscriptionCollectionAPI', 405

    def verify(self, config):
        # TODO: Implement a method to verify that the POST body is valid
        return True,{}

    # HTTP POST
    # POST should allow adding multiple instances to a collection.
    # For now, this only adds one instance.
    # TODO: 'id' should be obtained from the request data.
    def post(self):
        logging.info('SubscriptionCollectionAPI POST called')
        try:
            config = request.get_json(force=True)
            ok, msg = self.verify(config)
            if ok:
                members[config['Id']] = config
                resp = config, 201
            else:
                resp = msg, 400
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PATCH
    def patch(self):
        logging.info('SubscriptionCollectionAPI PATCH called')
        return 'PATCH is not a supported command for SubscriptionCollectionAPI', 405

    # HTTP DELETE
    def delete(self):
        logging.info('SubscriptionCollectionAPI DELETE called')
        return 'DELETE is not a supported command for SubscriptionCollectionAPI', 405
