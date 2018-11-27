# coding: UTF-8
import os
import sys
import re
import argparse
import pandas as pd
from datetime import datetime, date
import pytz
from manageiq_client.api import ManageIQClient as MiqApi
from manageiq_client.filters import Q
try:
    from io import BytesIO
except ImportError:
    from cStringIO import StringIO as BytesIO

url = os.environ.get('MIQURL') or 'http://localhost:3000/api'
username = os.environ.get('MIQUSERNAME') or 'admin'
password = os.environ.get('MIQPASSWORD') or 'smartvm'
token = os.environ.get('MIQTOKEN')

output_dir = "output/"
TZ = 'Asia/Tokyo'
jst = pytz.timezone(TZ)

client = None
if token:
    print("\nAuthenticating with the API token")
    client = MiqApi(url, dict(token=token))
else:
    print("\nAuthenticating with the user credentials")
    client = MiqApi(url, dict(user=username, password=password))

parser = argparse.ArgumentParser(description='CloudForms Report Result Collector')
parser.add_argument('--dry-run', '-n', action='store_const', dest='dryrun',
                    const=True, default=False,
                    help='do not dump files (dry-run); just show the report ids')
parser.add_argument('--from', '-f', '--start', '-s', dest='start_date_str', action='store',
                    nargs=1, default=None, help='start date YYYYMMDD of range for which results are collected')
parser.add_argument('--to', '-t', '--end', '-e', dest='end_date_str', action='store',
                    nargs=1, default=None, help='end date YYYYMMDD of range for which results are collected')
parser.add_argument('strings', metavar='names', nargs='*',
                    help='name of report to collect results')
args = parser.parse_args()

if args.start_date_str:
    naive = datetime.strptime(args.start_date_str[0] + " 00:00:00", "%Y%m%d %H:%M:%S")
    local_date = jst.localize(naive, is_dst=None)
    start_date = local_date.astimezone(pytz.utc)
else:
    start_date = datetime.fromtimestamp(0, pytz.utc)

if args.end_date_str:
    naive = datetime.strptime(args.end_date_str[0] + " 23:59:59", "%Y%m%d %H:%M:%S")
else:
    today = date.today()
    naive = datetime.strptime(today.strftime("%Y%m%d") + " 23:59:59", "%Y%m%d %H:%M:%S")
local_date = jst.localize(naive, is_dst=None)
end_date = local_date.astimezone(pytz.utc)

def dump_results(names, start_date, end_date):
    for result in client.collections.results.all:
        if (len(names) == 0 | (result.report[u'name'] in names)) & (start_date <= result.created_on) & (result.created_on <= end_date):
            name = result.report[u'name']
            print("Report \"{}\": result id {}".format(name, result.id))
            if args.dryrun == False:
                col_order = result.report[u'col_order']
                print("Order of Columns: {}".format(col_order))
                if len(result.result_set) > 0:
                    print("Writing saved report created on {}".format(result.created_on.astimezone(jst)))
                    df = pd.DataFrame(result.result_set)
                    filename = output_dir + re.sub(r'[ /:]', '_', result.report[u'name'] + "_") + result.created_on.astimezone(jst).strftime("%Y%m%d-%H") + ".csv"
                    df.to_csv(filename, columns=col_order)
                else:
                    print("Empty result set: skipping file creation")

print "Date Range"
print("Start date = {} (UTC: {})".format(start_date.astimezone(jst).strftime("%Y-%m-%d %H:%M:%S"), start_date.strftime("%Y-%m-%d %H:%M:%S")))
print("  End date = {} (UTC: {})".format(end_date.astimezone(jst).strftime("%Y-%m-%d %H:%M:%S"), end_date.strftime("%Y-%m-%d %H:%M:%S")))

names = []
if len(args.strings) > 0:
    filter = None
    for name in args.strings:
        names.append(name)

dump_results(names, start_date, end_date)
