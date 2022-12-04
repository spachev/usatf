#! /usr/bin/python

import requests
import urllib
import argparse
import sys
import lxml.html
from lxml import etree

parser = argparse.ArgumentParser()
parser.add_argument("--url-args", required=True)
parser.add_argument("--headers")
parser.add_argument("--extra-values")
args = parser.parse_args()


BASE_URL = "https://www.runnercard.com/results3/event?{}".format(args.url_args)
delim = ";"

# TODO parse headers from HTML
COLS =  args.headers.split(",") if args.headers else ["Place", "Bib", "Name", "City", "Place Gender", "Gender", "Place Div", "Div", "Gun Time"]

extra_values = args.extra_values.split(",") if args.extra_values else None
print(delim.join(COLS))

url = BASE_URL # for now
r = requests.get(url)
tree = lxml.html.fromstring(r.text)
els = tree.xpath("//table/tbody/tr")
for el in els:
	td_els = el.xpath("td")
	row = []
	for td_el in td_els:
		txt = td_el.text_content().strip()
		if not txt:
			continue
		row.append(txt)
	if extra_values:
		row += extra_values
	print(delim.join(row))

