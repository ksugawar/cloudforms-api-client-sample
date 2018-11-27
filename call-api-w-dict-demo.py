# coding: UTF-8
import os
import sys
import re
import argparse
from manageiq_client.api import ManageIQClient as MiqApi
from manageiq_client.filters import Q
from time import sleep
try:
    from io import BytesIO
except ImportError:
    from cStringIO import StringIO as BytesIO

url = os.environ.get('MIQURL') or 'http://localhost:3000/api'
username = os.environ.get('MIQUSERNAME') or 'admin'
password = os.environ.get('MIQPASSWORD') or 'smartvm'
token = os.environ.get('MIQTOKEN')

client = None
if token:
    print("\nAuthenticating with the API token")
    client = MiqApi(url, dict(token=token))
else:
    print("\nAuthenticating with the user credentials")
    client = MiqApi(url, dict(user=username, password=password))

params = { 
    'action_method': 'POST',
    'uri_parts': {
        'namespace': 'System',
        'class': 'Request',
        'instance': 'object_walker',
        'message': 'create'
    },
    'parameters': {
        'dict_arg': {
            'key1': 'val1',
            'foo': 'bar',
            'array': [ 1, 2, 3],
            'number': 12345,
            'boolean': True,
            'null': None
        }
    },
    'requester': {
        'auto_approve': True
    }
}

print("REST API payload = {}".format(params))

action = client.collections.automation_requests.action
requests = action.execute_action("create", **params)
request = next((item for item in requests if item), None)
results = request.reload(expand=True)
subcollections = request.subcollections
print("REST API Request = {}".format(request))
while True:
    request_task = client.get(request.href)
    print("REST API Request Task = {}".format(request_task))
    if request_task['request_state'] == 'finished':
        print("Request task finished")
        break
    sleep(1)
