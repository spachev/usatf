from util import *
import sys,csv
from db import DB
import argparse
import json
import re

def get_race(race_name, race_date, race_dist_cm):
	race = get_race_from_db(race_name, race_date)
	if race == None:
		if race_date == None or race_dist_cm == None:
			raise Exception("Race not found in the database, "
				+ "and date or distance not specified, cannot create")
		create_race(race_name, race_date, race_dist_cm)
	return get_race_from_db(race_name, race_date)

def get_race_from_db(race_name, race_date):
	q = "select * from usatf.race where name = '" + \
		con.escape(race_name) + "'"
	if	race_date:
		q += " and `date` = '" + con.escape(race_date) + "'"
	con.query(q)
	return con.fetch_row()

def create_race(race_name, race_date, race_dist_cm):
	q = "insert into usatf.race (name,`date`,dist_cm) values " + \
		"(%s,%s,%s)"
	con.query(q, (race_name, race_date, race_dist_cm))

class Members:
	def __init__(self, race_date):
		q = "select *,%s - year(bdate) - (date_format(bdate, %s) > %s) age from usatf.member"
		con.query(q, (race_date.year, "%m%d", race_date.strftime('%m%d')))
		self.members = {}
		r = con.fetch_row()
		while r:
			k = self.get_member_key(r)
			if k not in self.members:
				self.members[k] = []
			self.members[k].append(r)
			r = con.fetch_row()
		#print(self.members)
	@staticmethod
	def get_member_key(r):
		return str(r.lname).upper() + "|" + str(r.age) + "|" + str(r.gender).upper()[0:1];
	def find(self, row):
		k = self.get_member_key(row)
		#print("Checking key " + k)
		if k not in self.members:
			return None
		m_list = self.members[k]
		if len(m_list) == 1:
			return m_list[0]
		raise Exception("Multiple matches for " + str(row.__dict__) + ": " + str(m_list))

class Row_obj:
	def __init__(self, ref_o, row):
		fields = ref_o.__dict__.keys()
		fields.append('lname')
		for k in fields:
			self.__dict__[k] = ref_o.get_field(k, row)


class Ref_obj:
	def __init__(self, fields):
		fix_fields_re = re.compile(r"\s+")
		lc_fields = [fix_fields_re.sub("_", f.lower()) for f in fields]
		for f in ("place", "name", "gun_time", "chip_time", "gender", "age"):
			try:
				self.__dict__[f] = lc_fields.index(f)
			except:
				self.__dict__[f] = None

	def get_field(self, field_name, row):
		try:
			return row[self.__dict__[field_name]]
		except:
			if field_name == "lname":
				return row[self.name].split(' ')[-1]
			print("bad field: " + field_name)
			raise

	def get_row_obj(self, row):
		return Row_obj(self, row)

	def find_member(self, row):
		r_o = self.get_row_obj(row)
		return members.find(r_o)

if len(sys.argv) < 2:
	fatal("Missing file name argument")

parser = argparse.ArgumentParser(description='Manage races')
parser.add_argument('--file', help='Race CSV file', required=True)
parser.add_argument('--delim', help='CSV file field delimiter', default=';')
parser.add_argument('--race-name', help='Race Name', required=True)
parser.add_argument('--race-date', help='Race Date')
parser.add_argument('--race-dist-cm', help='Race Distance in centimiters')

args = parser.parse_args()

fname = args.file
con = DB()
con.connect()
race = get_race(args.race_name, args.race_date, args.race_dist_cm)
print(race)
members = Members(race.date)
print(sorted(members.members.keys()))

with open(fname, 'rb') as f:
	r = csv.reader(f, delimiter = args.delim)
	fields =  next(r)
	ref_o = Ref_obj(fields)
	#print(json.dumps(ref_o.__dict__))
	for row in r:
		m = ref_o.find_member(row)
		if m:
			print(row)
			print "matched to"
			print(m)

con.close()
