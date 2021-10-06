#! /usr/bin/env python

import requests
import lxml.html
from db import DB

con = DB()
con.connect()

for gender in ["men", "women"]:
	
	url = "https://www.usatf.org/events/2020/2020-u-s-olympic-team-trials-marathon/qualifying-standards/{}-s-marathon-performances".format(gender)
	print(gender.title())
	data = requests.get(url).text
	tree = lxml.html.fromstring(data)
	els = tree.xpath("//table/tbody/tr/td[1]")
	names = [el.text for el in els]

	query = "select concat(fname, ' ', lname) full_name " + \
		" from usatf.member having full_name in (" + ",".join(["%s" for name in names]) + ")"
	con.query(query, names)
	while True:
		r = con.fetch_row()
		if not r:
			break
		print(r.full_name)

    

