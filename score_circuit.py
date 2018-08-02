from util import *
from db import DB
import argparse
import datetime

class Member:
	def __init__(self, r):
		self.__dict__ = r.__dict__
		self.overall_points = 0
		self.div_points = 0
		self.masters_points = 0
		self.races = 0

class Scoreboard:
	def __init__(self):
		self.members = {}
		con.query("select * from usatf.member")
		while True:
			r = con.fetch_row()
			if not r:
				break
			self.members[r.id] = Member(r)

	def get_member(self, rr_rec):
		return self.members[rr_rec.member_id]

def score_race(r):
	print("Scoring race " + str(r.id))
	con.query("select * from usatf.race_results where race_id = %s",
						[int(r.id)])
	while True:
		rr_rec = con.fetch_row()
		if not rr_rec:
			break
		m = scoreboard.get_member(rr_rec)
		print(m.__dict__)


def score_circuit(year):
	#print("Scoring for " + str(year))
	races = get_races(year)
	#print(races)
	for r in races:
		score_race(r)

def get_races(year):
	con.query("select * from usatf.race where date between %s and %s",
						(str(year) + "-01-01", str(year) + "-12-31"))
	return con.fetch_all()

now = datetime.datetime.now()
parser = argparse.ArgumentParser(description='Score races')
parser.add_argument('--year', default=now.year, help='Year', required=False)
args = parser.parse_args()

con = DB()
con.connect()
scoreboard = Scoreboard()
#print(scoreboard.members)
score_circuit(args.year)
con.close()
