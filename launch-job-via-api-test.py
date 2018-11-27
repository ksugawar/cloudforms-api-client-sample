# coding: UTF-8
import os
import sys
import re
from manageiq_client.api import ManageIQClient as MiqApi
from manageiq_client.filters import Q
from time import sleep

# the next line assumes you're running this on the CFME appliance itself.
# If not, you need to add the parameter ssl_verify=False to the client
# MiqApi() initialization because CFME appliances use self-signed certs
# by default.
url = os.environ.get('MIQURL') or 'http://localhost:3000/api'
username = os.environ.get('MIQUSERNAME') or 'admin'
password = os.environ.get('MIQPASSWORD') or 'smartvm'
token = os.environ.get('MIQTOKEN')

# CF API Authentication (client initialization)
client = None
if token:
    print("\nAuthenticating with the API token")
    client = MiqApi(url, dict(token=token), verify_ssl=False)
else:
    print("\nAuthenticating with the user credentials")
    client = MiqApi(url, dict(user=username, password=password), verify_ssl=False)

payload = { 
    'action_method': 'POST',
    'uri_parts': {
        'namespace': 'AutomationManagement/AnsibleTower/Operations/StateMachines',
        'class': 'Job',
        # 'instance': 'default',
        'instance': 'autobranch', # This is a customized CF Automate instance (i.e. won't work out of the box)
        'message': 'create'
    },
    'parameters': {
        'job_template_name': 'hello-world',
        'vm_guid': '134ffccc-cc0d-4302-96c9-722eb84e7285', # Management Engine GUID of the target VM
        # 'ems_guid': '....', # Or the target provider's GUID
        'target': 'localhost', # (optional) parameter for limit (if ommitted vm_guid or ems_guid is used)
        'dialog_param_hello_world': 'Hello World' # extra variables to pass to the Job 
                                                  # you need to prefix variable name with dialog_param_
    },
    'requester': {
        'auto_approve': True
    }
}

print("REST API payload = {}".format(payload))

action = client.collections.automation_requests.action
requests = action.execute_action("create", **payload)

# Automation Request API can take multiple requests at once, so the return
# value is an array of requests. Here, we called the API with only one request,
# so we can safely assume that the returned array has only one element.
request = next((item for item in requests if item), None)

# We can get the latest status of the request by GET-ing the URI in request.href.
# Poll status until task.request_status changes from 'pending'
while True:
    request_task = client.get(request.href)
    print("REST API Request Task = {}".format(request_task))
    if request_task['request_state'] != 'pending':
        print("Request task active")
        break
    sleep(5)

# We know (by reading the CF Automate code) that CloudForms' state machine
# checks active request's status in 60s after the request_status becomes
# 'active'. We wait for 60s, too.
sys.stdout.write('Waiting for 60 seconds ...')
sys.stdout.flush()
sleep(60)
print

# Poll one in 5s til the request_status becomes 'finished'.
while True:
    request_task = client.get(request.href)
    print("REST API Request Task = {}".format(request_task))
    if request_task['request_state'] == 'finished':
        print("Request task finished")
        break
    sleep(5)
