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

from g import INDEX, INTERNAL_SERVER_ERROR

PRIMARY_BNAME = b'EventService'
BNAME = b'Subscriptions'

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
            # Find the entry with the correct value for Id
            resp = 404
            with g.db.view() as tx:
                event_service = tx.bucket(PRIMARY_BNAME)
                if event_service:
                        ident_bucket = event_service.bucket(BNAME).bucket(str(ident).encode())
                        if not ident_bucket:
                            resp = f"Subscription {ident} of EventService not found", 404
                        else:
                            value = ident_bucket.get(INDEX).decode()
                            resp = json.loads(value), 200
                else:
                    resp = f"EventService not found", 404
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
            resp = 404
            with g.db.update() as tx:
                eventservice = tx.bucket(PRIMARY_BNAME)
                if eventservice:
                    subscriptions = eventservice.bucket(BNAME)
                else:
                    return f"EventService not found", 404

                if not subscriptions:
                    subscriptions = eventservice.create_bucket(BNAME)

                if subscriptions:
                    subscriptions_ident = subscriptions.bucket(str(ident).encode())

                if subscriptions_ident:
                    return f"Subscription {ident} for EventService already exists", 404
                else:
                    subscriptions_ident = subscriptions.create_bucket(str(ident).encode())
                    subscriptions_ident.put(INDEX, json.dumps(request.json).encode())
                    resp = request.json, 201
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
            '@odata.id': "",
            '@odata.type': '#EventDestinationCollection.EventDestinationCollection',
            '@odata.context': self.rb + '$metadata#EventDestinationCollection.EventDestinationCollection',
            'Name': 'Event Destination  Collection',
            "Members": [],
            "Members@odata.count": 0
        }

    # HTTP GET
    def get(self):
        logging.info('SubscriptionCollectionAPI GET called')
        try:
            bucket_members = []
            with g.db.view() as tx:
                b = tx.bucket(PRIMARY_BNAME).bucket(BNAME)

                if not b:
                    resp = f'Subscription for EventServices not found', 404
                else:
                    for k, v in b:
                        if not v:
                            if b.bucket(k):
                                bucket_members.append(json.loads(b.bucket(k).get(INDEX).decode())['@odata.id'])
            self.config["@odata.id"] = "/redfish/v1/EventService/Subscriptions"
            self.config['Members'] = [{'@odata.id': x} for x in bucket_members]
            self.config["Members@odata.count"] = len(bucket_members)
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
