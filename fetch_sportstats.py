from sel import Sel
import argparse
import time

FIRST_COL_POS=3
LAST_COL_POS=11
RIEGEL_Q = 1.06

class SS_Fetcher(Sel):
	def __init__(self, race_id):
		Sel.__init__(self)
		self.url = "https://www.sportstats.us/display-results.xhtml?raceid=" \
			+ str(race_id)
		self.fix_q = None
		self.header_printed = False
		self.delim = ";"
		self.col_map = {"bib" : "Bib", "name" : "Name", "age": "Age", "finish" : "Time",
									"gender" : "Gender",
									"category" : "Div", "rank" : "Place", "gender place" : "Place Gender",
									"cat. place" : "Place Div"}
		self.cols = ["Bib", "Name", "Gender", "Div", "Place Overall",
				"Place Gender", "Place Div", "Time"]
		self.div_pos = self.cols.index("Div")

	def init_cols(self):
		els = self.find_many_by_xpath("//tr[@role='row']/th[@role='columnheader' and position() >= " +
			str(FIRST_COL_POS) + " and position() <= " + str(LAST_COL_POS) + "]/span/span")
		self.cols = []
		for i,el in enumerate(els):
			col_in_page = el.text
			col_name = self.col_map.get(col_in_page.lower(), col_in_page)
			self.cols.append(col_name)

	def set_fix_q(self, target_dist, actual_dist):
		self.fix_q = (float(target_dist) / float(actual_dist)) ** RIEGEL_Q
		self.cols.append("Adjusted Time")

	def fetch(self):
		self.get(self.url)
		self.parse_page()
		n_pages = self.get_n_pages()
		#print("Got {} pages".format(n_pages))
		for i in range(2,n_pages+1):
			el = self.find_by_xpath("//a[text()='{}']".format(i))
			self.remember_page()
			el.click()
			self.assert_in_page('Page {}'.format(i))
			self.parse_page()

	def get_n_pages(self):
		el = self.find_by_xpath("//p[contains(text(), 'Page')]")
		return int(el.text.split('/')[1].strip())

	def parse_page(self):
		self.init_cols()
		if not self.header_printed:
			print(self.delim.join(self.cols))
			self.header_printed = True
		els = self.find_many_by_xpath("//tr[@role='row']/td[@role='gridcell' and position() >= " +
			str(FIRST_COL_POS) + " and position() <= " + str(LAST_COL_POS) + "]")
		row = []
		for i,el in enumerate(els):
			row.append(el.text)
			if ":" in el.text:
				if self.fix_q != None:
					h,m,s = map(float,el.text.strip().split(":"))
					t = h * 3600 + m * 60 + s
					t_fixed = t * self.fix_q
					h_fixed = int(t_fixed / 3600)
					t_fixed -= h_fixed * 3600
					m_fixed = int(t_fixed / 60)
					t_fixed -= m_fixed * 60
					row.append("{:02d}:{:02d}:{:04.1f}".format(h_fixed, m_fixed, t_fixed))
			if (i + 1) % len(self.cols) == 0:
				lc_div = row[self.div_pos].lower()
				has_female = ("female" in lc_div or "athena" in lc_div or "filly" in lc_div)
				has_male = ((not "female" in lc_div and "male" in lc_div) or "clydesdale" in lc_div)
				if  has_male or has_female: # matches both male and female
					if has_female:
						gender = "f"
					else:
						gender = "m"
					row = row[:self.div_pos] + [gender] + row[self.div_pos:]
				print(self.delim.join(row))

				row = []


parser = argparse.ArgumentParser()
parser.add_argument("--race-id")
parser.add_argument("--target-dist")
parser.add_argument("--actual-dist")
args = parser.parse_args()
if not args.race_id:
	raise Exception("Missing race_id")


f = SS_Fetcher(args.race_id)
if args.target_dist and args.actual_dist:
	f.set_fix_q(args.target_dist, args.actual_dist)
f.fetch()
