# Copyright Notice:
# Copyright 2016-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# Declares global variables
#
# The canonical way to share information across modules within a single program
# is to create a special module (often called config or cfg). So this file
# should be called config.py.  But too late, now.

from flask import Flask, request
from flask_restful import Api
from functools import wraps
from jsonschema import validate, ValidationError
import time, json
from db_conn import DataBase


DB_FILEPATH = 'm7_database.db'


def delay_response():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with open('api_emulator/redfish/config.json') as f:
                jsonconfig = json.load(f)
            class_json = jsonconfig.get(func.__qualname__.split('.')[0])
            if class_json:
                method_json = class_json.get(func.__name__)
                if method_json:
                    delay = method_json.get('delay')
                    if delay:
                        time.sleep(delay)
                        print(f"{delay=}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def validate_json(schema):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                # Validate the JSON data against the schema
                validate(request.json, schema)
            except ValidationError as e:
                # If validation fails, return a 400 Bad Request response
                return {'error': str(e)}, 400
            # If validation succeeds, call the original function
            return f(*args, **kwargs)
        return wrapper
    return decorator

# Settings from emulator-config.json
#
staticfolders = []

# Base URI. Will get overwritten in emulator.py
rest_base = 'base'

# Create the databse object to store emulator configs
db = DataBase(DB_FILEPATH)
INDEX = b"index"

# Create Flask server
app = Flask(__name__)

# Create RESTful API
api = Api(app)
