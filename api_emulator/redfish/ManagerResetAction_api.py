# Copyright Notice:
# Copyright 2016-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# Singleton API: POST

import g
import requests
import os
import subprocess
import time

import sys, traceback, json, logging
from flask import Flask, request, make_response, render_template, jsonify
from flask_restful import reqparse, Api, Resource
from subprocess import check_output
from g import db, INDEX, INTERNAL_SERVER_ERROR

BNAME = b"Managers"
INDICES = [1]

class ManagerResetActionAPI(Resource):
    # kwargs is use to pass in the wildcards values to replace when the instance is created.
    def __init__(self, **kwargs):
        logging.info('ManagerResetActionAPI init called')
        pass
    
    # HTTP POST
    def post(self,ident):
        logging.info('ManagerResetActionAPI POST called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            manager_ident = bucket_hierarchy[:2]
            manager_data = g.get_value_from_bucket_hierarchy(manager_ident, INDICES)
            if not manager_data:
                logging.info(f"Manager {ident} not found")
                return f"Manager {ident} not found!", 400
            if not request.data:
                logging.info(f"No payload provided")
                json_payload = {}
                logging.info(f"Payload = {json_payload}")
                return {}, 200
            else:
                try:
                    json_payload = json.loads(request.data.decode("utf-8"))
                    action = json_payload.get("ResetType")
                    if action is None:
                        logging.info(f"ResetType not found")
                        return f"ResetType not provided in request payload", 400
                except Exception as e:
                    logging.info(f"invalid  or no JSON payload found : " + str(e))
                    return f"Invalid or no JSON payload passed", 400

            logging.info(f"Payload = {json_payload}")
            allowableResetTypes = manager_data["Actions"]["#Manager.Reset"]["ResetType@Redfish.AllowableValues"]
            if action not in allowableResetTypes:
                return f"""Invalid reset type!
ResetType, possible values:
{allowableResetTypes}""", 400
            if action == "GracefulRestart":
                print(f"Manager {ident} Gracefully restarted")
            elif action == "ForceRestart":
                print(f"Manager {ident} Forcefully restarted")
            return 'POST Action request completed', 200
        except Exception as e:
            traceback.print_exc()
            return "Internal Server error", INTERNAL_SERVER_ERROR

    # HTTP GET
    def get(self,ident):
        return 'GET is not supported', 405, {'Allow': 'POST'}

    # HTTP PATCH
    def patch(self,ident):
         return 'PATCH is not supported', 405, {'Allow': 'POST'}

    # HTTP PUT
    def put(self,ident):
         return 'PUT is not supported', 405, {'Allow': 'POST'}

    # HTTP DELETE
    def delete(self,ident):
         return 'DELETE is not supported', 405, {'Allow': 'POST'}
