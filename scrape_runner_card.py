#! /usr/bin/python

import requests
import urllib
import argparse
import sys
import lxml.html
from lxml import etree


# TODO: parametrize
BASE_URL="http://www.runnercard.com/results3/event?meetId=293ab9f2-4598-46e8-a7df-b4c53b8136da&eventId=928944a6-6115-48f6-85b4-d2185666f68a&startTimingPointId=178b707d-b599-4600-b75f-788c3e64e6f7&endTimingPointId=f1104039-1b48-4331-b47f-302f0ba489cc"
delim = ";"

COLS = ["Place", "Bib", "Name", "City", "Place Gender", "Gender", "Place Div", "Div", "Gun Time"]


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
	print(delim.join(row))

