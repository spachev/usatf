import requests
import urllib
import argparse
import sys
import json
import logging

#logging.basicConfig(level=logging.DEBUG)

BASE_URL="https://www.runsum.com/results/resframe_rpcjames.php?param1=runners&raceid={}&event1={}&visage=xxxxxoxxxxxxxxxxxxxxxxxxxxxxxxxxxoxxxxxxxxxxxxxxxxxxxxx&crit=&class1=all&limit=5000&offset=0"
COLS = ["Place", "Name", "Gender", "Gun Time"]
parser = argparse.ArgumentParser(description='Fetch Runsum Results')
parser.add_argument('--race-id', help='Race ID', required=True)
parser.add_argument('--event', help='Event', required=True)

args = parser.parse_args()

url = BASE_URL.format(args.race_id, urllib.quote(args.event))
r = requests.get(url, headers={'User-agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'})
#print(r.content)
rsp = r.json()
data = rsp['list']
delim = ";"
print(delim.join(COLS))

for d in data:
	l = [d['oplace'], d['first_name'] + ' ' + d['last_name'], d['gender'], d['time']]
	print(delim.join(l))






