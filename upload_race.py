from util import *
import sys,csv
from db import DB
import argparse
import json
import re
from age_grader import Age_grader
from constants import *

last_chip_time_ms = None
last_gun_time_ms = None
ROLLOVER_CUTOFF_MS = 2000 * 1000

age_grader = Age_grader()

def get_race(race_name, race_date, race_dist_cm):
	race = get_race_from_db(race_name, race_date)
	if race == None:
		if race_date == None or race_dist_cm == None:
			raise Exception("Race not found in the database, "
				+ "and date or distance not specified, cannot create")
		print("creating race")
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
		gender = gender.lower()[0]
		if gender not in ['m', 'f']:
			return
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
		self.members_by_lname = {}
		self.members_by_row_id = {}
		self.matches = {}
		r = con.fetch_row()
		while r:
			k = self.get_member_key(r)
			if k not in self.members:
				self.members[k] = []
			k_lname = self.get_member_lname_key(r)
			if k_lname not in self.members_by_lname:
				self.members_by_lname[k_lname] = []
			self.members_by_lname[k_lname].append(r)
			self.members[k].append(r)
			self.members_by_row_id[r.id] = r
			r = con.fetch_row()
		#print(self.members_by_lname)
		#print(self.members)
	@staticmethod
	def get_member_key(r):
		lname = cleanup_str(r.lname).split(" ")[-1]
		return lname.upper() + "|" + str(r.age) + "|" + str(r.gender).upper()[0:1]

	@staticmethod
	def get_member_lname_key(r):
		lname = cleanup_str(r.lname).split(" ")[-1]
		return lname.upper() + "|" + str(r.gender).upper()[0:1]

	#TODO: make more robust
	def maybe_match(self, el, r):
		if r.match_row_id:
			return r.match_row_id == el.id
		#print("maybe_match: name={} fname={}".format(r.name, el.fname))
		return r.name[0].upper() == el.fname[0].upper()

	def get_lname_match_list(self, r):
		k_lname = self.get_member_lname_key(r)
		return [el for el in self.members_by_lname[k_lname] if self.maybe_match(el, r)]

	def find_by_row_id(self, row_id):
		return self.members_by_row_id[row_id]

	def find_by_lname(self, r):
		k_lname = self.get_member_lname_key(r)
		#print("k_lname={}".format(k_lname))
		if r.age > 0 or not k_lname in self.members_by_lname:
			return None
		if not r.mark_for_match:
			match_list = self.get_lname_match_list(r)
			if match_list:
				print("Row {} could possibly match {}, mark it with * if you want it matched".
					format(r.__dict__, [el.__dict__ for el in match_list]))
				if args.force_manual_match:
					return self.manual_match(match_list, r, k_lname)
			return None
		match_list = self.members_by_lname[k_lname]
		if len(match_list) == 1:
			return match_list[0]
		match_list = self.get_lname_match_list(r)
		if len(match_list) == 1:
			return match_list[0]
		return self.manual_match(match_list, r, k_lname)

	def manual_match(self, m_list, row, k):
		while True:
			row_id = int(get_input("Multiple matches for " + str(row.__dict__) + ": " + str(m_list) + "\nenter Row id (0 for no match):"))
			if row_id == 0:
				return None
			for m in m_list:
				if m.id == row_id:
					self.matches[k] = row
					return m
				print("Bad row ID, try again")

	def find(self, row):
		if row.match_row_id:
			return self.find_by_row_id(row.match_row_id)
		k = self.get_member_key(row)
		if k in self.matches:
			print("Member " + str(k) + " already matched")
			return None
		# print("Checking key " + k)
		if k not in self.members:
			#print("no match for key " + k)
			return self.find_by_lname(row)
		m_list = self.members[k]
		if len(m_list) == 1:
			self.matches[k] = row
			return m_list[0]
		return self.manual_match(m_list, row, k)

class Row_obj:
	def __init__(self, ref_o, row):
		fields = ref_o.__dict__.keys()
		fields.append('lname')
		for k in fields:
			self.__dict__[k] = ref_o.get_field(k, row)
		try:
		  self.age = int(self.age)
		except:
		  fatal("Bad age {} in row {} ".format(self.age, row))
		self.usatf_age = 0
		self.mark_for_match = False

def adjust_for_rollover(last_time_ms, cur_time_ms):
	if last_time_ms and last_time_ms - cur_time_ms > ROLLOVER_CUTOFF_MS:
		return cur_time_ms + 3600 * 1000
	return cur_time_ms


class Race_rec:
	def __init__(self, ref_o, m, row_o):
		global last_gun_time_ms
		global last_chip_time_ms
		self.member_id = m.id
		self.member = m
		self.race_id = race.id
		self.dist_cm = race.dist_cm
		self.gun_time_ms = time_to_ms(row_o.gun_time)
		self.chip_time_ms = time_to_ms(row_o.chip_time)
		# self.place = parse_place(row_o.place)
		for k in ('overall', 'gender', 'div', 'gender_usatf', 'div_usatf',
						'masters', 'masters_usatf', 'gender_age_grade_usatf'):
			self.__dict__['place_' + k ] = 0
		self.gun_time_ms = adjust_for_rollover(last_gun_time_ms, self.gun_time_ms)
		self.chip_time_ms = adjust_for_rollover(last_chip_time_ms, self.chip_time_ms)
		last_chip_time_ms = self.chip_time_ms
		last_gun_time_ms = self.gun_time_ms


	def compute_age_grade(self, runner):
		self.age_grade = age_grader.grade_for_race(runner, self)

class Race_records:
	def __init__(self):
		self.records = []
	def add_record(self, r):
		self.records.append(r)
	def rank_age_graded_gender(self, gender):
		it = iter(sorted([r for r in self.records if r.member.gender.lower().startswith(gender) ], key=lambda r: -r.age_grade))
		place = 1
		for r in it:
			r.place_gender_age_grade_usatf = place
			place += 1

	def rank_age_graded(self):
		for gender in ['m', 'f']:
			self.rank_age_graded_gender(gender)

	def db_insert(self):
		if len(self.records) == 0:
			return
		r = self.records[0]
		con.query("delete from usatf.race_results where race_id = %s",
							[r.race_id])
		fields = list(k for k in r.__dict__ if k not in ('dist_cm','member'))
		row_expr = "(" + "%s," * (len(fields) - 1) + "%s)"
		q = "insert into usatf.race_results (" + ",".join(fields) + \
			") values " + (row_expr + ",") * (len(self.records) - 1) + row_expr
		vals = list((r.__dict__[k] for r in self.records for k in fields))
		print(vals)
		con.query(q, vals)

class Ref_obj:
	def __init__(self, fields):
		fix_fields_re = re.compile(r"\s+")
		lc_fields = [fix_fields_re.sub("_", f.lower().strip()) for f in fields]
		print(lc_fields)
		for f in ("place", "name", "gun_time", "chip_time", "gender", "age", "time",  "first_name",
			"last_name", "clock_time"):
			try:
				self.__dict__[f] = lc_fields.index(f)
			except:
				self.__dict__[f] = None
		if self.gun_time is None:
			self.gun_time = self.time
		if self.gun_time is None:
			self.gun_time = self.clock_time
		if self.place is None:
			self.place = lc_fields.index("place_overall")
	def __str__(self):
		return "{}".format(self.__dict__)

	def get_race_rec(self, m, row_o):
		return Race_rec(self, m, row_o)

	def get_field(self, field_name, row):
		try:
			if field_name == "time":
				print("time: {}".format(self.__dict__[field_name]))
				print(row)
				print(row[self.__dict__[field_name]])
			return row[self.__dict__[field_name]]
		except:
			if field_name == "age":
				return 0
			if field_name in ('first_name', 'last_name'):
				return None
			if field_name == "name":
				if self.first_name is not None and self.last_name is not None:
					return row[self.first_name] + " " + row[self.last_name]
			if field_name == "lname":
				if self.last_name is not None:
					return row[self.last_name]
				return row[self.name].split(' ')[-1]
			elif field_name in ("chip_time", "time", "clock_time") and self.gun_time != None:
				return row[self.gun_time]
			elif field_name in ("gun_time","clock_time") and self.time != None:
				print("row:" + ';'.join(row))
				print("time ind: " + str(self.time))
				return row[self.time]
			print("bad field: " + field_name)
			print("row:" + ';'.join(row))
			raise

	def find_member(self, row_o):
		return members.find(row_o)

def parse_place(p):
	try:
		return int(filter(str.isdigit, p))
	except:
		return 0

if len(sys.argv) < 2:
	fatal("Missing file name argument")

parser = argparse.ArgumentParser(description='Upload races')
parser.add_argument('--file', help='Race CSV file', required=True)
parser.add_argument('--delim', help='CSV file field delimiter', default=';')
parser.add_argument('--race-name', help='Race Name', required=True)
parser.add_argument('--race-date', help='Race Date')
parser.add_argument('--race-dist-cm', help='Race Distance in centimiters')
parser.add_argument('--force-manual-match', action='store_true', help='Force Manual Match')

args = parser.parse_args()

fname = args.file
con = DB()
con.connect()
race = get_race(args.race_name, args.race_date, args.race_dist_cm)
members = Members(race.date)
#print(sorted(members.members.keys()))
place_tracker = Place_tracker()
#print "div for 11 is " + str(place_tracker.get_div(11))
usatf_place_tracker = Place_tracker()
records = Race_records()

with open(fname, 'rb') as f:
	r = csv.reader(f, delimiter = args.delim)
	fields =  next(r)
	fields = [cleanup_str(f) for f in fields]
	print("fields: {}".format(fields))
	ref_o = Ref_obj(fields)
	print('ref_o: {}'.format(ref_o))
	for row in r:
		mark_for_match = False
		match_row_id = None
		if not row[0]:
			continue
		if row[0][0] == "*":
			no_star = row[0][1:]
			mark_for_match = True
			parts = no_star.split('!')
			if len(parts) == 2:
				row[0] = parts[1]
				match_row_id = int(parts[0])
				print("match_row_id={}".format(match_row_id))
				# 0 means ignore runner
				if int(parts[1]) == 0:
					continue
			else:
				row[0] = no_star
		row = [cleanup_str(v) for v in row]
		row_o = Row_obj(ref_o, row)
		row_o.usatf_age = row_o.age
		row_o.mark_for_match = mark_for_match
		row_o.match_row_id = match_row_id
		place_tracker.record_runner(row_o.gender, row_o.usatf_age)
		if not row_o.time:
			continue
		#print("searching for " + str(row_o.__dict__))
		m = ref_o.find_member(row_o)
		if m:
			row_o.usatf_age = int(m.usatf_age)
			#print(row_o.__dict__)
			race_r = ref_o.get_race_rec(m, row_o)
			race_r.compute_age_grade(m)
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
			print(row_o.__dict__)
			records.add_record(race_r)
	print("Inserting")
	records.rank_age_graded()
	records.db_insert()
con.close()
