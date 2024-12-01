#! /usr/bin/python

import requests
import urllib
import argparse
import sys
import lxml.html
from lxml import etree

MAGIC_HEADERS={'user-agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
			     'accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
			     'authority' : 'www.runnercard.com',
			     'accept-language' : 'en-US,en;q=0.6'}

def fetch_url(url, gender):
	res = []
	r = requests.get(url, headers=MAGIC_HEADERS)
	tree = lxml.html.fromstring(r.text)
	els = tree.xpath("//div[contains(@class, 'table-responsive')]/table[contains(@class,'table-striped') and contains(@style, 'width:inherit')]/tbody/tr")
	for el in els:
		td_els = el.xpath("td")
		row = []
		for td_el in td_els:
			txt = td_el.text_content().strip()
			row.append(txt)
		row.append(gender)
		if ":" in row[6]:
			res.append(row)
	return res


base_url = "https://www.runnercard.com/results3/"
meet_url = base_url + "meet?meetId=6e589705-d6d3-4c69-b4df-392bf924339d"
delim = ";"

r = requests.get(meet_url,
				 headers=MAGIC_HEADERS)
tree = lxml.html.fromstring(r.text)
els = tree.xpath("//p[contains(@class, 'lead')]/a[contains(text(), 'ns 5K')]")

data = []
for el in els:
	href = base_url + el.attrib["href"]
	gender = "M" if el.text[0] == "M" else "F"
	data += fetch_url(href, gender)

data.sort(key=lambda r: r[6])
print(delim.join(["Place", "Bib", "Name", "Blank", "Team Place", "Team", "Time", "Team Place", "Blank", "Gender"]))
for r in data:
	print(delim.join(r))

