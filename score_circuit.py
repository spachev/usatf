from util import *
from db import DB
import argparse
import datetime
from constants import *

class Member:
	def __init__(self, r):
		self.__dict__ = r.__dict__
		self.overall_points = 0
		self.div_points = 0
		self.masters_points = 0
		self.races = 0
		self.usatf_age = int(self.usatf_age)

	def fits_in_div(self, gender, div):
		if self.gender.lower() != gender.lower():
			return False
		if div == "overall" or div == "div":
			return True
		if div == "masters" and self.usatf_age < 40:
			return False
		return True # for now


class Scoreboard:
	def __init__(self, year):
		self.members = {}
		self.races = None
		self.race_lists = {}
		self.placing_fields = ['fname', 'lname', 'place', 'points']
		self.field_display = {'fname' : 'First Name', 'lname': 'Last Name',
			'place' : 'Circuit Place', 'points':'Circuit Points'
		}
		self.div_part_names = {'overall':'Overall', 'm': 'Men', 'f':'Women',
			'masters':'Masters'}
		self.div_lists_by_race = {}
		con.query("select *," + usatf_age_expr() + " from usatf.member", (year, "%m%d",
							USATF_MEM_DATE))
		while True:
			r = con.fetch_row()
			if not r:
				break
			self.members[r.id] = Member(r)

	def get_div_list(self):
		return range(0, len(DIV_CUTOFFS))

	def get_display_val(self, m, k, div, r):
		if k in ["place", "points"]:
			k += "_" + str(div) + "_" + str(r.id)
		return str(m.__dict__[k])

	def html_field_headers(self):
		return "<tr><td>" + "</td><td>".join(
			self.field_display[k] for k in self.placing_fields) + "</td></tr>"

	def html_member_placing_for_race(self, m, div, r):
		return "<tr><td>" + \
		"</td><td>".join(self.get_display_val(m, k, div, r) \
		for k in self.placing_fields) + \
		"</td></tr>"

	def get_member(self, rr_rec):
		return self.members[rr_rec.member_id]

	def append_to_race_list(self, r, m):
		if not r.id in self.race_lists:
			self.race_lists[r.id] = []
		self.race_lists[r.id].append(m)

	def build_div_lists_for_race(self, r):
		l = {}
		for m in self.race_lists[r.id]:
			for t in ["overall", "masters", "div"]:
				for gender in ["m", "f"]:
					div = t + "_" + gender
					if t == "div":
						div = str(self.get_div_code(m.usatf_age)) + "_" + gender
					#print("genders:" + m.gender + "," + gender)
					if m.fits_in_div(gender, t):
						self.append_to_div_for_race(l, r, m, div)
		#print("l keys =" + str(l.keys()))
		self.div_lists_by_race[r.id] = l

	def get_div_code(self, age):
		for i in range(0, len(DIV_CUTOFFS)):
			if age < DIV_CUTOFFS[i]:
				return i
		return i + 1

	def append_to_div_for_race(self, l, r, m, div):
		if div == "div":
			div = str(self.get_div_code(m.usatf_age))
		k = div + "_" + str(r.id)
		if not k in l:
			l[k] = []
		l[k].append(m)
		#print("append, l=" + str(l))

	def build_div_lists(self):
		for r in self.races:
			self.build_div_lists_for_race(r)

	def get_div_name(self, div):
		parts = div.split("_")
		return " ".join(self.div_part_name(p) for p in parts)

	def get_div_name_by_code(self, code):
		code = int(code)
		if code == 0:
			return str(DIV_CUTOFFS[0]) + " and under"
		if code == len(DIV_CUTOFFS):
			return str(DIV_CUTOFFS[-1] + 1) + " and older"
		return str(DIV_CUTOFFS[code - 1] + 1) + "-" + str(DIV_CUTOFFS[code])

	def div_part_name(self, p):
		if p in self.div_part_names:
			return self.div_part_names[p]
		return self.get_div_name_by_code(p)

	def html_div_scoring_for_race(self, r, gender, div):
		full_div = str(div) + "_" + gender.lower()
		k =  full_div + "_" + str(r.id)
		#print(self.div_lists_by_race)
		if not k in self.div_lists_by_race[r.id]:
			return ""
		html =  "<tr><td class='circuit_title' colspan='100%'>" + \
			self.get_div_name(full_div) + "</td></tr>\n"
		html += scoreboard.html_field_headers()
		for m in self.div_lists_by_race[r.id][k]:
			html += self.html_member_placing_for_race(m, div, r)
		return html

	def html_div_scoring(self, gender, div):
		html = ""
		for r in self.races:
			html += self.html_div_scoring_for_race(r, gender, div)
		return html

def get_points(place):
	if place > PLACE_POINTS_CUTOFF or place <= 0:
		return 0
	if place >= PLACE_HOP_CUTOFF:
		return PLACE_POINTS_CUTOFF - place + 1
	place_diff = PLACE_HOP_CUTOFF - place + 1
	return (PLACE_POINTS_CUTOFF - PLACE_HOP_CUTOFF) + place_diff * (place_diff + 1) / 2

def get_points_key(t, r):
	return "points_" + t + "_" + str(r.id)

def get_place_key(t, r):
	return "place_" + t + "_" + str(r.id)

def score_race(r):
	html = "<table class='circuit' align='center'>\n"
	html += "<tr><th colspan='100%'>" + str(r.name) + "</th></tr>\n"
	con.query("select * from usatf.race_results where race_id = %s order by place_overall",
						[int(r.id)])
	while True:
		rr_rec = con.fetch_row()
		if not rr_rec:
			break
		m = scoreboard.get_member(rr_rec)
		scoreboard.append_to_race_list(r, m)
		for t in ["gender", "masters", "div"]:
			t_key = t
			if t == "div":
				t_key = str(scoreboard.get_div_code(m.usatf_age))
			if t == "gender":
				t_key = "overall"
			k_points = get_points_key(t_key, r)
			k_place = get_place_key(t_key, r)
			place = rr_rec.__dict__["place_" + t + "_usatf"]
			m.__dict__[k_points] = get_points(place)
			m.__dict__[k_place] = place
		#print(m.__dict__)
	scoreboard.build_div_lists()
	for t in ["overall", "masters"] + scoreboard.get_div_list():
		for gender in ['m', 'f']:
			html += scoreboard.html_div_scoring(gender, t)
	html += "</table>"
	return html

def get_circuit_css():
	return """
	<style>
	table.circuit
	{
		border: 1px solid black;
		border-collapse: collapse;
	}
	table.circuit th,td
	{
		border: 1px solid black;
		padding: 5px;
	}
	.circuit_title
	{
		text-align: center;
		font-weight: bold;
	}
	</style>
"""

def score_circuit(year):
	#print("Scoring for " + str(year))
	scoreboard.races = get_races(year)
	#print(races)
	print(get_circuit_css())
	for r in scoreboard.races:
		print(score_race(r))

def get_races(year):
	con.query("select * from usatf.race where date between %s and %s",
						(str(year) + "-01-01", str(year) + "-12-31"))
	return con.fetch_all()

def test_get_points():
	for i in range(1,30):
		print "place " + str(i) + ": " + str(get_points(i)) + " points"

def test_div_names():
	for code in range(0, len(DIV_CUTOFFS) + 1):
		print("code = " + str(code) + " name = " + scoreboard.get_div_name_by_code(code))

now = datetime.datetime.now()
parser = argparse.ArgumentParser(description='Score races')
parser.add_argument('--year', default=now.year, help='Year', required=False)
args = parser.parse_args()

con = DB()
con.connect()
scoreboard = Scoreboard(args.year)
#print(scoreboard.members)
score_circuit(args.year)
con.close()