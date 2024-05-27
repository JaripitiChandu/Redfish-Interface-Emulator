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


#
# Database configs
INDEX = b"index"
DB_FILEPATH = 'm7_database.db'

# Create the databse object to store emulator configs
db = DataBase(DB_FILEPATH)


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


def get_value_from_bucket_hierarchy(buckets): 
    with db.view() as bucket:
        for bucket_name in buckets:
            bucket = bucket.bucket(str(bucket_name).encode())
            if not bucket:
                message = ' '.join(buckets[:buckets.index(bucket_name)+1]) + ' not found'
                print(message)
                return False, message
        else:
            value = bucket.get(INDEX).decode()
            return True, json.loads(value)


def get_collection_from_bucket_hierarchy(buckets):
    bucket_members = []
    with db.view() as bucket:
        for bucket_name in buckets:
            bucket = bucket.bucket(str(bucket_name).encode())
            if not bucket:
                message = ' '.join(buckets[:buckets.index(bucket_name)+1]) + ' not found'
                print(message)
                return False, message
        else:
            for k, v in bucket:
                if not v:
                    if bucket.bucket(k):
                        bucket_members.append(json.loads(bucket.bucket(k).get(INDEX).decode())['@odata.id'])
    return True, bucket_members


def is_required_bucket_hierarchy_present(buckets):
    with db.view() as bucket:
        for bucket_name in buckets:
            bucket = bucket.bucket(str(bucket_name).encode())
            if not bucket:
                message = ' '.join(buckets[:buckets.index(bucket_name)+1]) + ' not found'
                print(message)
                return False, message
        else:
            return True, 'all required buckets present'


def is_not_resource_bucket_already_present_in_hierarchy(buckets):
    with db.view() as bucket:
        for bucket_name in buckets:
            bucket = bucket.bucket(str(bucket_name).encode())
            if not bucket:
                break
        else:
            message = ' '.join(buckets[:buckets.index(bucket_name)+1]) + ' already exists'
            return False, message
    return True, 'bucket hierarchy not present'


def post_value_to_bucket_hierarchy(buckets, value):
    with db.update() as bucket:
        for bucket_name in buckets:
            if not bucket.bucket(str(bucket_name).encode()):
                bucket = bucket.create_bucket(str(bucket_name).encode())
            else:
                bucket = bucket.bucket(str(bucket_name).encode())
        bucket.put(INDEX, str(value).encode())


# Settings from emulator-config.json
#
staticfolders = []

# Base URI. Will get overwritten in emulator.py
rest_base = 'base'

# Create the databse object to store emulator configs
db = DataBase(DB_FILEPATH)
INDEX = b"index"
INTERNAL_SERVER_ERROR = "Internal Server Error", 500

# db.print_db()

# Create Flask server
app = Flask(__name__)

# Create RESTful API
api = Api(app)
