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
from api_emulator.utils import update_nested_dict


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


def get_index(indices, idx):
    if max(indices)<idx:
        raise Exception(f"Invalid Arguments indices = {indices}, idx = {idx}")
    for i in indices:
        if idx<=i:
            return i

def get_value_from_bucket_hierarchy(buckets, indices):
    """
    Retrieve a value from the bucket hierarchy.

    Args:
        buckets (list): List of bucket names representing the hierarchy.

    Returns:
        tuple: A tuple containing a boolean indicating success or failure,
        and a message indicating the result or error.
    """
    with db.view() as bucket:
        for i, bucket_name in enumerate(buckets):
            bucket = bucket.bucket(str(bucket_name).encode())
            if not bucket:
                idx = get_index(indices, i)
                return rest_base+'/'.join(map(str, buckets[:idx+1])) + ' not found', 404
        else:
            value = bucket.get(INDEX).decode()
            return json.loads(value), 200


def get_collection_from_bucket_hierarchy(buckets, indices=None):
    """
    Retrieve a collection from the bucket hierarchy.

    Args:
        buckets (list): List of bucket names representing the hierarchy.

    Returns:
        tuple: A tuple containing a boolean indicating success or failure,
        and a message or list of bucket members.
    """
    bucket_members = []
    with db.view() as bucket:
        for i, bucket_name in enumerate(buckets):
            bucket = bucket.bucket(str(bucket_name).encode())
            if not bucket:
                # if this bucket isn't final collection bucket
                if i+1 != len(buckets):
                    if indices:
                        if max(indices)<i:
                            return True, bucket_members
                        idx = get_index(indices, i)
                        message = rest_base+'/'.join(map(str, buckets[:idx+1])) + ' not found'
                    else:
                        message = rest_base+'/'.join(map(str, buckets)) + ' not found'
                    return False, message
                # if it is final collection bucket
                else:
                    return True, bucket_members
        else:
            for k, v in bucket:
                if not v:
                    if bucket.bucket(k):
                        bucket_members.append(json.loads(bucket.bucket(k).get(INDEX).decode())['@odata.id'])
    return True, bucket_members


def is_required_bucket_hierarchy_present(buckets, indices):
    """
    Check if the required bucket hierarchy is present.

    Args:
        buckets (list): List of bucket names representing the hierarchy.

    Returns:
        tuple: A tuple containing a boolean indicating success or failure,
        and a message indicating the result or error.
    """
    with db.view() as bucket:
        for i, bucket_name in enumerate(buckets):
            bucket = bucket.bucket(str(bucket_name).encode())
            if not bucket:
                idx = get_index(indices, i)
                message = rest_base+'/'.join(map(str, buckets[:idx+1])) + ' not found'
                return False, message
        else:
            return True, 'all required buckets present'

def post_value_to_bucket_hierarchy(buckets, indices, value, post=True):
    """
    Post a value to the bucket hierarchy.

    Args:
        buckets (list): List of bucket names representing the hierarchy.
        value: Value to be posted to the hierarchy.

    Returns:
        None
    """
    if len(indices)>1:
        split1, split2 = buckets[:indices[-2]+1], buckets[indices[-2]+1:]
        present, message = is_required_bucket_hierarchy_present(buckets[:indices[-2]+1], indices[:-1]) 
        if not present:
            return message, 404
    else:
        split1, split2 = tuple(), buckets

    with db.update() as bucket:
        for bucket_name in split1:
            bucket = bucket.bucket(str(bucket_name).encode())
        for bucket_name in split2:
            temp = bucket.bucket(str(bucket_name).encode())
            if not temp:
                temp = bucket.create_bucket(str(bucket_name).encode())
            bucket = temp
        if bucket.get(INDEX) and post:
            return rest_base+'/'.join(map(str, buckets)) + ' already exists', 409
        bucket.put(INDEX, json.dumps(value).encode())
        return value, 201

def patch_bucket_value(buckets, indices, payload):
    value, status = get_value_from_bucket_hierarchy(buckets, indices)
    if status == 404:
        return value, status
    update_nested_dict(value, payload)
    post_value_to_bucket_hierarchy(buckets, indices, value, post=False)
    return value, 200

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
