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
from .Manager_api import members as manager_members

members={}

INTERNAL_ERROR = 500

class ManagerResetActionAPI(Resource):
    # kwargs is use to pass in the wildcards values to replace when the instance is created.
    def __init__(self, **kwargs):
        logging.info('ManagerResetActionAPI init called')
        pass
    
    # HTTP POST
    def post(self,ident):
        logging.info('ManagerResetActionAPI POST called')
        try:
            if ident not in manager_members:
                logging.info(f"ident not found")
                return f"Manager {ident} not found!", 400
            logging.info(f"{request.data}")
            try:
                json_payload = json.loads(request.data.decode("utf-8"))
                action = json_payload.get("ResetType")
                if action is None:
                    logging.info(f"action not found")
                    return f"ResetType not provided in request payload", 400
            except Exception as e:
                logging.info(f"invalid  not found : " + str(e))
                return f"Invalid or no JSON payload passed", 400
            logging.info(f"Payload = {json_payload}")
            allowableResetTypes = manager_members[ident]["Actions"]["#Manager.Reset"]["ResetType@Redfish.AllowableValues"]
            if action not in allowableResetTypes:
                return f"""Invalid reset type!
ResetType, possible values:
{allowableResetTypes}""", 400
            if action == "ForceOff":
                self.force_off(manager_members, ident)
            elif action == "On":
                self.force_on(manager_members, ident)
            elif action == "ForceRestart":
                self.force_off(manager_members, ident)
                self.force_on(manager_members, ident)
                print(f"Manager {ident} restarted")
            return 'POST Action request completed', 200
        except Exception as e:
            traceback.print_exc()
            return "Internal Server error", INTERNAL_ERROR

    @staticmethod
    def force_off(manager_members, ident):
        if manager_members[ident]["PowerState"] == "On":
            manager_members[ident]["PowerState"] = "resetting"
            manager_members[ident]['Status']['State'] = "resetting"
            time.sleep(10)
            manager_members[ident]["PowerState"] = "Off"
            manager_members[ident]['Status']['State'] = "Disabled"
            print (f'Manager {ident} Powered Off')
        else:
            print(f"Manager {ident} is already Powered Off")

    @staticmethod
    def force_on(manager_members, ident):
        if manager_members[ident]["PowerState"] == "Off":
            manager_members[ident]["PowerState"] = "resetting"
            manager_members[ident]['Status']['State'] = "resetting"
            time.sleep(10)
            manager_members[ident]["PowerState"] = "On"
            manager_members[ident]['Status']['State'] = "Enabled"
            print (f'System {ident} Powered On')
        else:
            print(f"System {ident} is already Powered On")

    # HTTP GET
    def get(self,ident):
        print ('ResetAction')
        print (members)
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
