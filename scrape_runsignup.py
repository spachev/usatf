import requests
import urllib
import argparse
import sys
import json
import lxml.html
import re
from util import *

BASE_URL = "https://runsignup.com/Race/Results/{}"
HEADER_MAP = {"name" : "Name", "place" : "Place", "gender": "Gender", "age" : "Age", "chip_time" : "Time"}

def get_results_for_div(result_set_id):
	url = BASE_URL.format(race_id) + "?resultSetId={}&page=1&num=100".format(result_set_id)
	rsp = requests.get(url, headers={'accept': 'application/json'})
	#print("Resutls:")
	print(rsp.text)
	data = rsp.json()
	headings = data['headings']
	h_lookup = {}
	pos = 0
	for h in headings:
		h_lookup[h["key"]] = pos
		pos += 1
	rows = []
	for el in data['resultSet']['results']:
		r = {}
		for k in h_lookup:
			r[k] = el[h_lookup[k]]
		rows.append(r)
	return rows

def get_result_set_ids(race_id):
	url = BASE_URL.format(race_id)
	rsp = requests.get(url)
	tree = lxml.html.fromstring(rsp.text)
	els = tree.xpath("//a[contains(@href, 'resultSetId=')]")
	ids = []
	for el in els:
		if "dog" in el.text_content().lower():
			continue
		href = el.get("href")
		m = re.search(r'resultSetId=(\d+)', href)
		if not m:
			continue
		ids.append(m.group(1))
	return ids

def remove_dup_bibs(res):
	new_res = []
	for r in res:
		if new_res and r["bib_num"] == new_res[-1]["bib_num"]:
			continue
		new_res.append(r)
	return new_res

def fix_division(div):
	return div.split("\n")[-1]

def add_gender_and_age(data):
	for r in data:
		if "division" not in r:
			continue
		r["division"] = fix_division(r["division"])
		if "gender" not in r:
			r["gender"] = r["division"][0]
		if "age" not in r:
			r["age"] = r["division"][1:3] + "-" + r["division"][3:5]

parser = argparse.ArgumentParser()
parser.add_argument("--race-id", required=True)
parser.add_argument("--delim", default=";")
parser.add_argument("--result-set-id", default=None)
parser.add_argument("--min-result-set-id", type=int, default=0)
args = parser.parse_args()
race_id = args.race_id
delim = args.delim
result_set_id = args.result_set_id

min_result_set_id = args.min_result_set_id
combined = []
result_set_ids = get_result_set_ids(race_id) if result_set_id is None else [result_set_id]
if min_result_set_id:
    result_set_ids = [ result_set_id for result_set_id in result_set_ids if int(result_set_id) >= min_result_set_id ]
for id in result_set_ids:
	div_res = get_results_for_div(id)
	combined += div_res


combined = remove_dup_bibs(sorted(combined, key=lambda r: time_to_ms(r["chip_time"])))
add_gender_and_age(combined)

place = 1
for r in combined:
	r["place"] = place
	place += 1

print(delim.join([ HEADER_MAP[k] for k in HEADER_MAP]))
for r in combined:
	print(delim.join([str(r[k]) for k in HEADER_MAP]))
