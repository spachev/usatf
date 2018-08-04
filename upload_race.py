from util import *
import sys,csv
from db import DB
import argparse
import json
import re
from constants import *

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

class Place_tracker:
	def __init__(self):
		self.div_cutoffs = DIV_CUTOFFS
		self.divs =  self.div_cutoffs + ["", str(MAX_AGE), "MASTSERS"]
		self.cur_places = { gender + str(age) : 0 for gender
												 in ('m','f') for age in self.divs }
		self.cur_places[''] = 0
		self.reset_last_places()

	def inc_div(self, div_name, mode):
		#print("inc_div:" + div_name + "," + mode)
		self.cur_places[div_name] += 1
		self.last_places[mode] = self.cur_places[div_name]

	def get_last_place(self, mode):
		return self.last_places[mode]

	def get_div(self, age):
		for cutoff in self.div_cutoffs:
			#print("checking " + str(age) + " against cutoff " + str(cutoff))
			if age <= cutoff:
				return str(cutoff)
		return str(MAX_AGE)

	def reset_last_places(self):
		self.last_places = {}

	def record_runner(self, gender, age):
		self.reset_last_places()
		age = int(age)
		self.inc_div('', 'overall')
		self.inc_div(gender, 'gender')
		self.inc_div(gender + self.get_div(age), 'div')
		if age >= 40:
			#print("recording master")
			self.inc_div(gender + 'MASTSERS', 'masters')

class Members:
	def __init__(self, race_date):
		q = "select *,%s - year(bdate) - (date_format(bdate, %s) > %s) usatf_age " + \
			" , %s - year(bdate) - (date_format(bdate, %s) > %s) age" + \
			" from usatf.member"
		con.query(q, (race_date.year, "%m%d", USATF_MEM_DATE,
								race_date.year, "%m%d", race_date.strftime("%m%d")))
		self.members = {}
		self.matches = {}
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
		return str(r.lname).upper() + "|" + str(r.age) + "|" + str(r.gender).upper()[0:1]

	def find(self, row):
		k = self.get_member_key(row)
		if k in self.matches:
			raise Exception("Member " + str(k) + " already matched")
		#print("Checking key " + k)
		if k not in self.members:
			return None
		m_list = self.members[k]
		if len(m_list) == 1:
			self.matches[k] = row
			return m_list[0]
		raise Exception("Multiple matches for " + str(row.__dict__) + ": " + str(m_list))

class Row_obj:
	def __init__(self, ref_o, row):
		fields = ref_o.__dict__.keys()
		fields.append('lname')
		for k in fields:
			self.__dict__[k] = ref_o.get_field(k, row)
		self.age = int(self.age)
		self.usatf_age = 0

class Race_rec:
	def __init__(self, ref_o, m, row_o):
		self.member_id = m.id
		self.race_id = race.id
		self.gun_time_ms = time_to_ms(row_o.gun_time)
		self.chip_time_ms = time_to_ms(row_o.chip_time)
		# self.place = parse_place(row_o.place)
		for k in ('overall', 'gender', 'div', 'gender_usatf', 'div_usatf',
						'masters', 'masters_usatf'):
			self.__dict__['place_' + k ] = 0

class Race_records:
	def __init__(self):
		self.records = []
	def add_record(self, r):
		self.records.append(r)
	def db_insert(self):
		if len(self.records) == 0:
			return
		r = self.records[0]
		fields = list(k for k in r.__dict__)
		row_expr = "(" + "%s," * (len(fields) - 1) + "%s)"
		q = "insert into usatf.race_results (" + ",".join(fields) + \
			") values " + (row_expr + ",") * (len(self.records) - 1) + row_expr
		vals = list((r.__dict__[k] for r in self.records for k in fields))
		print(vals)
		con.query(q, vals)

class Ref_obj:
	def __init__(self, fields):
		fix_fields_re = re.compile(r"\s+")
		lc_fields = [fix_fields_re.sub("_", f.lower()) for f in fields]
		for f in ("place", "name", "gun_time", "chip_time", "gender", "age"):
			try:
				self.__dict__[f] = lc_fields.index(f)
			except:
				self.__dict__[f] = None

	def get_race_rec(self, m, row_o):
		return Race_rec(self, m, row_o)

	def get_field(self, field_name, row):
		try:
			return row[self.__dict__[field_name]]
		except:
			if field_name == "lname":
				return row[self.name].split(' ')[-1]
			print("bad field: " + field_name)
			raise

	def find_member(self, row_o):
		return members.find(row_o)

def parse_place(p):
	try:
		return int(filter(str.isdigit, p))
	except:
		return 0

def time_to_ms(t):
	print(t)
	parts = str(t).split(':')
	res = 0
	for p in parts:
		res = res * 60.0 + float(p)
	return int(res * 1000)

if len(sys.argv) < 2:
	fatal("Missing file name argument")

parser = argparse.ArgumentParser(description='Upload races')
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
#print(sorted(members.members.keys()))
place_tracker = Place_tracker()
usatf_place_tracker = Place_tracker()
records = Race_records()

with open(fname, 'rb') as f:
	r = csv.reader(f, delimiter = args.delim)
	fields =  next(r)
	ref_o = Ref_obj(fields)
	for row in r:
		row_o = Row_obj(ref_o, row)
		row_o.usatf_age = row_o.age
		place_tracker.record_runner(row_o.gender, row_o.usatf_age)
		m = ref_o.find_member(row_o)
		if m:
			row_o.usatf_age = int(m.usatf_age)
			print(row_o.__dict__)
			race_r = ref_o.get_race_rec(m, row_o)
			usatf_place_tracker.record_runner(row_o.gender, row_o.usatf_age)
			modes = ['overall', 'div', 'gender']
			usatf_modes = modes[:]
			if row_o.usatf_age >= 40:
				usatf_modes += ['masters']
				#print("Last places")
				#print(place_tracker.last_places)
			if row_o.age >= 40:
				modes += ['masters']
			for mode in modes:
				race_r.__dict__['place_' + mode] = place_tracker.get_last_place(mode)
			for mode in usatf_modes:
				race_r.__dict__['place_' + mode + '_usatf'] = usatf_place_tracker.get_last_place(mode)
			print(race_r.__dict__)
			records.add_record(race_r)
	print("Inserting")
	records.db_insert()
con.close()
