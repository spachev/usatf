from util import *
from db import DB
import argparse
import datetime
import re
import csv
from constants import *
from util import *


class Member:
	def __init__(self, r):
		self.__dict__ = r.__dict__
		self.overall_points = 0
		self.div_points = 0
		self.masters_points = 0
		self.gender_age_grade_points = 0
		self.races = 0
		self.usatf_age = int(self.usatf_age)

	def update_bonus_points(self):
		if DISABLE_BONUS:
			return
		if self.races <= BONUS_POINTS_DOUBLE_CUTOFF:
			self.bonus_points = self.races
			return
		self.bonus_points = BONUS_POINTS_DOUBLE_CUTOFF + \
			(self.races - BONUS_POINTS_DOUBLE_CUTOFF) * 2

	def update_total_points(self):
		for t in ['overall', 'masters', 'div', 'gender_age_grade']:
			points_var = t + "_points"
			total_points_var = t + "_total_points"
			self.__dict__[points_var] = 0
			if t == "div":
				t = scoreboard.get_div_code(self.usatf_age)
			self.__dict__[points_var] = sum(sorted((self.get_points_for_race(r,t)
				for r in scoreboard.races),reverse=True)[0:MAX_RACES])
			#if "age_grade" in points_var:
			#	print("age_grade={}".format(self.__dict__))
			self.__dict__[total_points_var] = self.__dict__[points_var]
			if not DISABLE_BONUS:
				 self.__dict__[total_points_var] += self.bonus_points

	def update_mars(self):
		for t in ['overall', 'masters', 'div', 'gender_age_grade']:
			self.update_mars_for_div(t)

	def get_points_for_race(self, r, div):
		if not r:
			return 0
		k = get_points_key(div, r)
		if not k in self.__dict__:
			return 0
		return self.__dict__[k]

	def set_best_mar(self, div, r, val):
		self.__dict__[get_best_mar_key(div, r)] = val

	def set_best2_mar(self, div, r, val):
		self.__dict__[get_best2_mar_key(div, r)] = val

	def set_best_hmar(self, div, r, val):
		self.__dict__[get_best_hmar_key(div, r)] = val

	def mul_points_for_race(self, div, r, val):
		#print(self.__dict__)
		k = get_points_key(div, r)
		self.__dict__[k] *= val

	def update_mars_for_div(self, t):
		best_race = None
		best2_race = None
		if t == "masters" and self.usatf_age < MASTERS_AGE:
			return
		if t == "div":
			t = scoreboard.get_div_code(self.usatf_age)
		div = t
		mars = [r for r in scoreboard.races if r.dist_cm == MAR_DIST_CM and
			self.get_points_for_race(r, div) > 0]
		mars.sort(key=lambda r: self.get_points_for_race(r, div), reverse = True)
		#print("Memeber: " + str(self.__dict__))
		#print("Marathons: " + str(mars))
		if len(mars) < 1:
			return
		best_race = mars[0]
		if len(mars) >= 2:
			best2_race = mars[1]
		self.set_best_mar(div, best_race, False)
		if best2_race:
			self.set_best2_mar(div, best2_race, False)
		if best_race:
			self.mul_points_for_race(div, best_race, 1.5)
			self.set_best_mar(div, best_race, True)
		if best2_race:
			self.mul_points_for_race(div, best2_race, 1.25)
			self.set_best2_mar(div, best2_race, True)

	def update_hmars_for_div(self, t):
		best_race = None
		if t == "masters" and self.usatf_age < MASTERS_AGE:
			return
		if t == "div":
			t = scoreboard.get_div_code(self.usatf_age)
		div = t
		for r in scoreboard.races:
			if int(r.dist_cm) != HMAR_DIST_CM:
				continue
			if self.get_points_for_race(best_race, div) < \
					self.get_points_for_race(r, div):
				if best_race:
					self.set_best_hmar(div, best_race, False)
				best_race = r
			else:
				self.set_best_hmar(div, r, False)
		if best_race:
			self.mul_points_for_race(div, best_race, 1.25)
			self.set_best_hmar(div, best_race, True)

	def update_hmars(self):
		for t in ['overall', 'masters', 'div']:
			self.update_hmars_for_div(t)

	def get_div_code(self):
		return scoreboard.get_div_code(self.usatf_age)

	def fits_in_div(self, gender, div):
		if self.gender.lower() != gender.lower():
			return False
		if div == "overall" or div == "div":
			return True
		if div == "masters":
			return self.usatf_age >= 40
		if "age_grade" in str(div):
			return True
		if (type(div) == int or div.isdigit()) and \
			int(div) == self.get_div_code():
				return True
		return False


class Scoreboard:
	def __init__(self, year):
		self.members = {}
		self.races = None
		self.rr_lookup = {}
		self.race_lists = {}
		self.common_placing_fields = ['place', 'fname', 'lname', 'points']
		self.race_placing_fields =  self.common_placing_fields + ['time', 'usatf_age', 'age_grade']
		self.placing_fields = self.common_placing_fields + ['races']
		if not DISABLE_BONUS:
			self.placing_fields += ['bonus_points']
		self.placing_fields += ['total_points']
		self.field_display = {'fname' : 'First Name', 'lname': 'Last Name',
			'place' : 'Circuit Place', 'points':'Regular Points',
			'races' : 'Races',
			'bonus_points':'Bonus Points', 'total_points': 'Total Points',
			'time' : 'Time',
			'age_grade': 'Age Grade %',
			'usatf_age': 'USATF age',
		}
		self.div_part_names = {'overall':'Overall', 'm': 'Men', 'f':'Women',
			'masters':'Masters', 'gender_age_grade': 'Age Grade'}
		self.div_lists_by_race = {}
		age_year = year
		if age_year == 2020:
			age_year += 1 # COVID
		con.query("select *," + usatf_age_expr() + " from usatf.member", (age_year, "%m%d",
							USATF_MEM_DATE))
		while True:
			r = con.fetch_row()
			if not r:
				break
			self.members[r.id] = Member(r)
			self.rr_lookup[r.id] = {}

	def get_div_list(self):
		return range(0, len(DIV_CUTOFFS))

	def general_div(self, div):
		if type(div) == int or div.isdigit():
			return "div"
		if "age_grade" in str(div):
			return "gender_age_grade"
		return div

	def get_display_val(self, m, k, div, r = None):
		if k == "time":
			return ms_to_time(self.rr_lookup[m.id][r.id].chip_time_ms) if r else None
		if "age_grade" in k:
			return "{:.2f}".format(self.rr_lookup[m.id][r.id].age_grade) if r else None
		if div == 'age_grade':
			div = 'gender_age_grade'
		if k in ["place", "points", "total_points"]:
			if r == None:
				k = self.general_div(div) + "_" + k
			else:
				k += "_" + str(div) + "_" + str(r.id)
		if k == "bonus_points" and DISABLE_BONUS:
			return ""
		return str(m.__dict__[k])

	def html_field_headers(self, r):
		if r:
			fields = self.race_placing_fields
		else:
			fields = self.placing_fields
		return "<tr><td>" + "</td><td>".join(
			self.field_display[k] for k in fields) + "</td></tr>"

	def html_member_placing_for_race(self, m, div, r):
		return "<tr><td>" + \
		"</td><td>".join(self.get_display_val(m, k, div, r) \
		for k in self.race_placing_fields) + \
		"</td></tr>"

	def record_rr_for_member(self, m, rr_rec):
		self.rr_lookup[m.id][rr_rec.race_id] = rr_rec

	def get_member(self, rr_rec):
		return self.members[rr_rec.member_id]

	def append_to_race_list(self, r, m):
		if not r.id in self.race_lists:
			self.race_lists[r.id] = []
		self.race_lists[r.id].append(m)

	def build_div_lists_for_race(self, r):
		l = {}
		if r.id not in self.race_lists:
			return
		for m in self.race_lists[r.id]:
			for t in ["overall", "masters", "div", "gender_age_grade"]:
				for gender in ["m", "f"]:
					div = t + "_" + gender
					if t == "div":
						div = str(self.get_div_code(m.usatf_age)) + "_" + gender
					#print("genders:" + m.gender + "," + gender)
					if m.fits_in_div(gender, t):
						self.append_to_div_for_race(l, r, m, div)
		for gender in ["m", "f"]:
			k = "age_grade_" + gender + "_" + str(r.id)
			#print([el.__dict__ for el in l[k]])
			age_grade_k = 'place_gender_age_grade_{}'.format(r.id)
			if k in l:
				l[k] = sorted(l[k], key=lambda el: el.__dict__[age_grade_k])
		self.div_lists_by_race[r.id] = l

	def get_div_code(self, age):
		for i in range(0, len(DIV_CUTOFFS)):
			if age <= DIV_CUTOFFS[i]:
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
		if "age_grade" in div:
			return "Age Graded"
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
		if not r:
			return self.html_div_scoring_total(gender, div)
		full_div = str(div) + "_" + gender.lower()
		k =  full_div + "_" + str(r.id)
		if r.id not in self.div_lists_by_race or not k in self.div_lists_by_race[r.id]:
			return ""
		html =  "<tr><td class='circuit_title' colspan='100%'>" + \
			self.get_div_name(full_div) + "</td></tr>\n"
		html += scoreboard.html_field_headers(r)
		for m in self.div_lists_by_race[r.id][k]:
			html += self.html_member_placing_for_race(m, div, r)
		return html

	def update_scores(self):
		for m_key in self.members:
			m = self.members[m_key]
			m.update_mars()
			m.update_hmars()
			m.update_bonus_points()
			m.update_total_points()

	def html_member_placing_overall(self, m, div):

		return "<tr><td>" + \
		"</td><td>".join(self.get_display_val(m, k, div) \
			for k in self.placing_fields) + \
			"</td></tr>"

	def html_div_scoring_total(self, gender, div):
		runners = []
		k = self.general_div(div) + "_total_points"
		for m_key in self.members:
			m = self.members[m_key]
			if not m.fits_in_div(gender, div):
				continue
			if k not in m.__dict__ or not m.__dict__[k]:
				continue
			runners.append(m)
		runners = sorted(runners, key = lambda m: m.__dict__[k], reverse = True)
		if len(runners) == 0:
			return ""
		place_k = self.general_div(div) + "_place"
		for place,r in enumerate(runners, 1):
			r.__dict__[place_k] = place
		full_div = str(div) + "_" + gender.lower()
		div_name = self.get_div_name(full_div)
		html = "<tr><td class='circuit_title' colspan='100%'>" + div_name + "</tr>\n"
		html += self.html_field_headers(None)
		for m in runners:
			html += self.html_member_placing_overall(m, div)
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
	if "age_grade" in str(t):
		t = "gender_age_grade"
	return "points_" + str(t) + "_" + str(r.id)

def get_best_mar_key(div, r):
	return "best_mar_" + str(div) + "_" + str(r.id)

def get_best2_mar_key(div, r):
	return "best2_mar_" + str(div) + "_" + str(r.id)

def get_best_hmar_key(div, r):
	return "best_hmar_" + str(div) + "_" + str(r.id)

def get_place_key(t, r):
	return "place_" + t + "_" + str(r.id)

def score_race(r):
	con.query("select * from usatf.race_results where race_id = %s order by place_overall",
						[int(r.id)])

	while True:
		rr_rec = con.fetch_row()
		if not rr_rec:
			break
		m = scoreboard.get_member(rr_rec)
		scoreboard.record_rr_for_member(m, rr_rec)
		scoreboard.append_to_race_list(r, m)
		for t in ["gender", "masters", "div", "gender_age_grade"]:
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
		m.races += 1

		#print(m.__dict__)
	scoreboard.build_div_lists_for_race(r)

def get_race_name(r):
	if r:
		return RACE_NAME_FIX_RE.sub("", str(r.name))
	return "Total scores"

def html_race_tag(r):
	if not r:
		return "race_all"
	return "race_" + str(r.id)

def html_race_anchor(r):
	return "<a name='" + html_race_tag(r) + "'></a>\n"

def html_race_link(r):
	return "<a href='#" + html_race_tag(r) + "'>" + get_race_name(r) + "</a>"

def html_race_scores(r):
	html = html_race_anchor(r) + "<table class='circuit' align='center'>\n"
	html += "<tr><th colspan='100%'>" + get_race_name(r) + "</th></tr>\n"
	divs = ["overall"]
	if SHOW_AGE_GRADE:
		divs.append("gender_age_grade")
	if SHOW_MASTERS:
		divs.append("masters")
	for t in divs + scoreboard.get_div_list():
		for gender in ['m', 'f']:
			html += scoreboard.html_div_scoring_for_race(r, gender, t)
	html += "</table>"
	return html

def get_circuit_css():
	return """
	<style>
	table.circuit
	{
		border: 1px solid black;
		border-collapse: collapse;
		margin-bottom: 10px;
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
	for r in scoreboard.races:
		score_race(r)
	scoreboard.update_scores()
	races = [None] + scoreboard.races # None for total
	html = get_circuit_css()
	races_html = ""
	links_html = ""
	for r in races:
		links_html += html_race_link(r) + "<br/>"
		races_html += html_race_anchor(r) + html_race_scores(r)
	html += "<div align='center'>" + links_html + "</div>" + races_html
	print(html)

def get_races(year):
	year = int(year)
	start_year = year
	end_year = year
	if start_year == 2020:
		end_year += 1 # COVID
	con.query("select * from usatf.race where date between %s and %s",
						(str(start_year) + "-01-01", str(end_year) + "-12-31"))
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
RACE_NAME_FIX_RE = re.compile("\\s*" + str(args.year) +"\\s*")

con = DB()
con.connect()
scoreboard = Scoreboard(args.year)
#print(scoreboard.members)
score_circuit(args.year)
con.close()
