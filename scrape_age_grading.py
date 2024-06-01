#! /usr/bin/python

import requests
import lxml.html
import csv
import datetime
import sys

from util import *
from constants import *

URL = "https://runbundle.com/tools/age-grading-calculator"
SAMPLE_PACE_KM = 300
MIN_AGE = 5
MAX_AGE = 100
KM_IN_MILE = 1.60934
DIST_LIST = ["1 M", "5 K", "10 K", "15 K", "10 M", "Half Marathon", "Marathon"]
HEADER = ["Event", "Event", "Kilometers","Miles","WR Seconds"]
WR_POS = len(HEADER)-1

def info(msg):
	print("[" + str(datetime.datetime.now()) + "] " + str(msg))


def get_dist_val(name):
	parts = name.split(" ")
	try:
		mul = KM_IN_MILE if parts[1].startswith("M") else 1
		return float(parts[0]) * mul * 1000
	except:
		if parts[0] == "Half":
			return HMAR_DIST_CM / 100
		if name == "Marathon":
			return MAR_DIST_CM / 100
		raise Exception("Invalid distance {}".format())

def get_grade_info(age, gender, dist):
	t = ms_to_time(dist * SAMPLE_PACE_KM)
	data = {
		"sex" : "male" if gender.lower().startswith('m') else 'female',
		"run-surface" : "road",
		"age" : age,
		"run-distance-units" : "metres",
		"run-time-input" : t,
		"submit" : "Calculate",
		"run-distance-input" : dist,
		"road-distance-select-input" : "",
		"track-distance-select-input" : "",
	}

	rsp = requests.post(URL, data=data)
	html = rsp.text
	tree = lxml.html.fromstring(html)
	els = tree.xpath("//table[@id='age-grading-results']//th[contains(text(),'Age-factor')]//following-sibling::*[1]")
	r = float(els[0].text)
	els = tree.xpath("//table[@id='age-grading-results']//th[contains(text(),'Open-class-standard')]//following-sibling::*[1]")
	wr_sec = time_to_ms(els[0].text)/1000
	return r,wr_sec

def read_ag_csv(fname):
	with open(fname, "r") as fh:
		data = {}
		csv_r = csv.reader(fh)
		header = next(csv_r)
		for r in csv_r:
			data[r[0]] = r
		return data

def update_data(data):
	for gender in ["M", "F"]:
		for dist in DIST_LIST:
			event_name = gender + dist
			dist_m = get_dist_val(dist)
			dist_km = float(dist_m) / 1000
			dist_miles = dist_km / KM_IN_MILE
			wr_sec = 0
			if not event_name in data:
				data[event_name] = [event_name, dist, dist_km, dist_miles, 0]
			row = data[event_name]
			data_pos = len(HEADER)
			row[WR_POS] = 0
			for age in range(MIN_AGE, MAX_AGE+1):
				updated = False
				if data_pos >= len(row) or not row[data_pos] or not row[WR_POS]:
					info("looking up {} age {}".format(event_name, age))
					r,wr_sec = get_grade_info(age, gender, dist_m)
					updated = True
				row[WR_POS] = wr_sec
				if len(row) <= data_pos:
					row.append(r)
				elif updated:
					row[data_pos] = r
				data_pos += 1

def write_ag_csv(fname, data):
	with open(fname, "w") as fh:
		header = HEADER + [str(age) for age in range(MIN_AGE, MAX_AGE+1)]
		csv_w = csv.writer(fh)
		csv_w.writerow(header)
		for k in data:
			csv_w.writerow(data[k])

#print(get_grade_info(48, "m", 21097.5))
#sys.exit(0)
fname = "age-grade.csv"
data = read_ag_csv(fname)
update_data(data)
write_ag_csv(fname, data)
