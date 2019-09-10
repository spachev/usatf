import requests
import urllib
import argparse
import sys
import json

BASE_URL="http://www.runsum.com/results/resframe_rpcjames.php?param1=runners&raceid={}&event1={}&visage=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxooxxxxxxxxxxxxxxxxxxxx&crit=&class1=all&limit=5000&offset=0"
COLS = ["Place", "Name", "Gender", "Age", "Gun Time"]
parser = argparse.ArgumentParser(description='Fetch Runsum Results')
parser.add_argument('--race-id', help='Race ID', required=True)
parser.add_argument('--event', help='Event', required=True)

args = parser.parse_args()

url = BASE_URL.format(args.race_id, urllib.quote(args.event))
r = requests.get(url)
rsp = r.json()
data = rsp['list']
delim = ";"
print(delim.join(COLS))

for d in data:
	l = [d['oplace'], d['first_name'] + ' ' + d['last_name'], d['gender'], d['age'], d['time']]
	print(delim.join(l))






