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
        'guid': 'cb62132b-9c89-49ba-8abb-e4f2a6ec5c33',
    },
    'vm_fields': {
        'number_of_cpus': 1,
        'cores_per_socket': 1,
        'vm_name': 'api-test-001',
        'vm_memory': '1024',
        'network_adapters': 1,
        'vlan': 'VM Network',
        'sysprep_custom_spec': 'rhel_customization',
        'sysprep_spec_override': True,
        'linux_host_name': 'api-test-001',
        'number_of_vms': 1,
        'provision_type': 'vmware',
        'schedule_type': 'immediately',
        'retirement': 0,
    },
    'requester': {
        'user_name': 'admin',
        'owner_email': 'admin@example.com',
        'auto_approve': True
    },
    'tags': {
    },
    'additional_values': {
        'placement_auto': True
    },
    'ems_custom_attributes': { },
    'miq_custom_attributes': { }
}

print("REST API payload = {}".format(payload))

action = client.collections.provision_requests.action
requests = action.execute_action("create", **payload)

request = next((item for item in requests if item), None)

while True:
    request_task = client.get(request.href)
    print("REST API Request Task = {}".format(request_task))
    if request_task['request_state'] != 'pending':
        print("Request task active")
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
