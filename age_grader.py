AGE_GRADE_FILE="age-grade.csv"
AGE_GRADE_EVENT_POS = 0

import csv
from util import *
from constants import *

class Age_grader:
	def __init__(self):
		self.col_map = {}
		self.dist_data = {}
		with open(AGE_GRADE_FILE, "r") as fp:
			csv_r = csv.reader(fp)
			h = next(csv_r)
			pos = 0
			for c in h:
				self.col_map[c] = pos
				pos += 1
			for row in csv_r:
				self.dist_data[row[AGE_GRADE_EVENT_POS]] = row
	def get_param(self, event, param):
		return float(self.dist_data[event][self.col_map[param]])

	def get_event_name(self, dist_cm, gender):
		dist_name = None
		if dist_cm == MAR_DIST_CM:
			dist_name = "Marathon"
		elif dist_cm == HMAR_DIST_CM:
			dist_name = "Half Marathon"
		elif dist_cm % MILE_DIST_CM == 0:
			dist_miles = dist_cm / MILE_DIST_CM
			dist_name = "{} M".format(dist_miles)
		else:
			dist_name = "{} K".format(dist_cm / 100000)
		return gender.upper() + dist_name

	def grade_for_race(self, runner, race_rec):
		dist_cm = race_rec.dist_cm
		time_ms = race_rec.chip_time_ms
		gender =  runner.gender
		age = runner.age
		event = self.get_event_name(dist_cm, gender)
		return self.grade_ms(event, age, time_ms)

	def grade(self, event, age, time):
		t = time_to_ms(time)
		return self.grade_ms(event, age, t)

	def grade_ms(self, event, age, t_ms):
		t = t_ms / 1000
		t_wr = self.get_param(event, 'WR Seconds')
		age = int(age)
		if age < 5:
			age = 5
		if age > 100:
			age = 100
		age_q = self.get_param(event, str(age))
		t_wr_age = t_wr / age_q
		return 100.0 * (t_wr_age / t)

def test_age_grader():
	ag = Age_grader()
	tests = (
		('M5 K', 48, "18:00"),
		('M5 K', 41, "15:39"),
		('M5 K', 21, "15:39"),
		('M5 K', 20, "15:39"),
		('M5 K', 18, "15:39"),
		('M5 K', 19, "15:39"),
		('MMarathon', 40, "2:37:58"),
		('F5 K', 45, '24:45'),
		('F5 K', 17, '19:55'),
		('F1 M', 17, '6:00'),
		('M1 M', 20, '4:40'),
		('M1 M', 20, '4:00'),
	)

	for t in tests:
		print("{} {}".format(t, ag.grade(*t)))

if __name__ == "__main__":
	test_age_grader()
