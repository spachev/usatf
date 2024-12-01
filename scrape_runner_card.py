#! /usr/bin/python

import requests
import urllib
import argparse
import sys
import lxml.html
from lxml import etree


# TODO: parametrize
#BASE_URL="http://www.runnercard.com/results3/event?meetId=293ab9f2-4598-46e8-a7df-b4c53b8136da&eventId=928944a6-6115-48f6-85b4-d2185666f68a&startTimingPointId=178b707d-b599-4600-b75f-788c3e64e6f7&endTimingPointId=f1104039-1b48-4331-b47f-302f0ba489cc"

#BASE_URL="https://www.runnercard.com/results3/event?meetId=f381d42b-3675-4ebd-a3ed-c036b8dc4643&eventId=75821a60-9735-4f62-ba66-ddb7c5453f1f&startTimingPointId=2ad99941-7d57-4ecd-8747-464044bbcf23&endTimingPointId=81a8650d-d6cb-4e9c-82fe-4c5fc2d63b5c"
BASE_URL = "https://www.runnercard.com/results3/event?meetId=7a06675b-81ad-47c5-ba80-2f31411170ff&eventId=a06f202c-40a0-4e7a-9227-09f98af99c3f&startTimingPointId=bbcaf398-1dbd-47cd-8580-1f9d787d5e35&endTimingPointId=8a0f8b94-5777-474e-9cd9-19b77d5d6088"
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
	if row[0].startswith("D"):
		continue
	print(delim.join(row))

