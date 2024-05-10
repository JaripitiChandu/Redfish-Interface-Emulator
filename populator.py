# iterate through folder structure of dump 
# extract index.json that are not collections 

import os
import json
import requests

ROOT_FOLDER = 'api_emulator/redfish/static/'
ENDPOINTS_TO_SKIP = []
REDFISH_URL = 'http://10.0.2.15:5000/redfish/v1/'


def post_call(url, data):
    # Convert the data to JSON format
    json_data = json.dumps(data)

    # Set the headers to specify that you're sending JSON data
    headers = {'Content-Type': 'application/json'}

    # Make the POST request
    response = requests.post(url, data=json_data, headers=headers)

    # Check the response
    if response.status_code == 200 or response.status_code == 201:
        print("POST request successful")
        print("Response:", response.json())
        return True
    else:
        print("POST request failed with status code:", response.status_code)
        return False


def find_index_json_files(root_folder):
    index_json_files = []
    for folder_name, subfolders, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename == "index.json":
                file_path = os.path.join(folder_name, filename)
                content = json.load(open(file_path))
                if 'Collection' not in content.get('@odata.type', '') :
                    index_json_files.append(file_path)
    return index_json_files

## find and store index json files that are not a collection 
# index_json_files = find_index_json_files(ROOT_FOLDER)
# for file_path in index_json_files:
#     print("Found index.json file:", file_path)
# print(len(index_json_files))


# read index files from list stored in file
with open('out_index.txt') as f:
    for path in f.read().split('\n'):
        # skip commented line
        if path.startswith('#'):
            continue
        # form url from json path
        url = path.replace(ROOT_FOLDER, REDFISH_URL).replace('/index.json', '')
        data = json.load(open(os.path.join(os.path.dirname(__file__), path)))
        print(url)
        print(path)
        
        if not post_call(url, data):
            break
