# Copyright Notice:
# Copyright 2016-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# EventService API File

"""
Singleton  API:  GET, POST
"""

import g

import sys, traceback
import logging, json
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource

# Resource and SubResource imports
from .templates.EventService import get_EventService_instance
from .Subscriptions_api import SubscriptionCollectionAPI, SubscriptionAPI

from g import INDEX, INTERNAL_SERVER_ERROR

PRIMARY_BNAME=b'EventService'

# EventService Singleton API
class EventServiceAPI(Resource):

    def __init__(self, **kwargs):
        logging.info('EventServiceAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR

    # HTTP GET
    def get(self):
        logging.info('EventServiceAPI GET called')
        try:
            resp = 404
            with g.db.view() as tx:
                eventservice = tx.bucket(PRIMARY_BNAME)
                if not eventservice:
                    resp = f"EventService not found", 404
                else:
                    value = eventservice.get(INDEX).decode()
                    resp = json.loads(value), 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self):
        logging.info('EventServiceAPI PUT called')
        return 'PUT is not a supported command for EventServiceAPI', 405

     # HTTP POST
    def post(self):
        logging.info('EventServiceAPI POST called')
        try:
            resp = 404
            with g.db.update() as tx:
                eventservice = tx.bucket(PRIMARY_BNAME)
                if eventservice:
                    resp = f"EventService already exists", 404
                else:
                    eventservice = tx.create_bucket(PRIMARY_BNAME)
                    eventservice.put(INDEX, json.dumps(request.json).encode())
                    resp = request.json, 201
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PATCH
    def patch(self):
        logging.info('EventServiceAPI PATCH called')
        patch_data = request.get_json(force=True)
        logging.info(f"Payload = {patch_data}")
        try:
            # Update specific portions of the identified object
            with g.db.update() as tx:
                eventservice = tx.bucket(PRIMARY_BNAME)
                if not eventservice:
                    return f"EventService not found", 404
                else:
                    event_data = json.loads(eventservice.get(INDEX).decode())

                    for key, value in patch_data.items():
                        if key in event_data:
                            event_data[key] = value

                    eventservice.put(INDEX, json.dumps(event_data).encode())
                    resp = event_data, 200

        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP DELETE
    def delete(self):
        logging.info('EventServiceAPI DELETE called')
        return 'DELETE is not a supported command for EventServiceAPI', 405
