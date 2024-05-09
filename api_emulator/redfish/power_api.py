# Copyright Notice:
# Copyright 2016-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# Power API File

"""
Collection API:  (None)
Singleton  API:  GET, PATCH
"""

import g

import sys, traceback
import logging
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource

members = {}

INTERNAL_ERROR = 500


# Power API
class PowerAPI(Resource):

    # kwargs is used to pass in the wildcards values to be replaced
    # when an instance is created via get_<resource>_instance().
    #
    # The call to attach the API establishes the contents of kwargs.
    # All subsequent HTTP calls go through __init__.
    #
    # __init__ stores kwargs in wildcards, which is used to pass
    # values to the get_<resource>_instance() call.
    def __init__(self, **kwargs):
        logging.info('PowerAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

    # HTTP GET
    def get(self, ident):
        logging.info('PowerAPI GET called')
        try:
            # Find the entry with the correct value for Id
            resp = 404
            if ident in members:
                resp = members[ident], 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self, ident):
        logging.info('PowerAPI PUT called')
        return 'PUT is not a supported command for PowerAPI', 405

    # HTTP POST
    def post(self, ident):
        logging.info('PowerAPI POST called')
        try:
            config=request.json
            members[ident]=config
            resp = config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp
        return 'POST is not a supported command for PowerAPI', 405

    # HTTP PATCH
    def patch(self, ident):
        logging.info('PowerAPI PATCH called')
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
        logging.info('PowerAPI DELETE called')
        return 'DELETE is not a supported command for PowerAPI', 405


# PowerCollection API
# Power does not have a collection API

