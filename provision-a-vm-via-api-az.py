# coding: UTF-8
import os
import sys
import re
from manageiq_client.api import ManageIQClient as MiqApi
from manageiq_client.filters import Q
from time import sleep

url = os.environ.get('MIQURL') or 'http://localhost:3000/api'
username = os.environ.get('MIQUSERNAME') or 'admin'
password = os.environ.get('MIQPASSWORD') or 'smartvm'
token = os.environ.get('MIQTOKEN')

# CF API 認証
client = None
if token:
    print("\nAuthenticating with the API token")
    client = MiqApi(url, dict(token=token))
else:
    print("\nAuthenticating with the user credentials")
    client = MiqApi(url, dict(user=username, password=password))

payload = { 
    'action_method': 'POST',
    'version': '1.1',
    'template_fields': {
        'guid': 'e56d90db-213a-47e7-943a-5a99f92e8f17',
        'name': 'az-rhel7-image',
        'request_type': 'template',
    },
    'vm_fields': {
        'provision_type': 'azure',
        'vm_name': 'az-api-test',
        'placement_auto': False,
        'resource_group': 1000000000001,
        'cloud_network': 1000000000001,
        'cloud_subnet': 1000000000001,
        'security_groups': [1000000000004],
        'floating_ip_address': -1,
        'number_of_vms': 1,
        'retirement': 0,
        'retirement_warn': 604800,
        'instance_type': 1000000000040,
        'addr_mode': 'dhcp',
        'root_username': 'ksugawar',
        'root_password': 'v2:{S2OPjMkKdpyiLcxiCwPsfQ==}',
    },
    'requester': {
        'user_name': 'admin',
        'owner_email': 'admin@example.com',
        'auto_approve': False,
    },
    'tags': {},
    'additional_values': {},
    'ems_custom_attributes': {},
    'miq_custom_attributes': {},
}

print("REST API payload = {}".format(payload))

action = client.collections.provision_requests.action
requests = action.execute_action("create", **payload)

request = next((item for item in requests if item), None)

while True:
    request_task = client.get(request.href)
    print("REST API Request Task = {}".format(request_task))
    if request_task['request_state'] != 'pending':
        print("Request task {}".format(request_task['request_state']))
        break
    sleep(5)

sys.stdout.write('Waiting for 60 seconds ...')
sys.stdout.flush()
sleep(60)
print

# request_status が 'finished' に変化するまで5秒に1回ポーリング
while True:
    request_task = client.get(request.href)
    print("REST API Request Task = {}".format(request_task))
    if request_task['request_state'] == 'finished':
        print("Request task finished")
        break
    sleep(5)
