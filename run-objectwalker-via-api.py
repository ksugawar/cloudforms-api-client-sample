# coding: UTF-8
import os
from manageiq_client.api import ManageIQClient as MiqApi

url = os.environ.get('MIQURL') or 'http://localhost:3000/api'
username = os.environ.get('MIQUSERNAME') or 'admin'
password = os.environ.get('MIQPASSWORD') or 'smartvm'
token = os.environ.get('MIQTOKEN')

client = None

if token:
    print("\nAuthenticating with the API token")
    client = MiqApi(url, dict(token=token))
else:
    print("\nAuthenticating with the user credentials: "+username+" / "+password)
    client = MiqApi(url, dict(user=username, password=password))

print("\nManageIQ version: {0}".format(client.version))

params = { 
    "action_method": "POST",
    "uri_parts": {
        "namespace": "System",
        "class": "Request",
        "instance": "object_walker",
        "message"   : "create"
    },
    "parameters" : {
        "var1" : "value 1",
        "var2" : "value 2",
        "minimum_memory" : 2048
    },
    "requester" : {
        "auto_approve" : True
    }
}

action = client.collections.automation_requests.action
action.execute_action("create", **params)

