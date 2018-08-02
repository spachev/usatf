from util import *
import mysql.connector

class DB:
	def __init__(self):
		self.var_dict = {'host' : 'localhost', 'db':'usatf', 'user':'usatf',
				'pw':'usatf'}
		for k,v in self.var_dict.items():
			self.__dict__[k] = get_config_var('DB_' + k.upper(), v)
		self.con = None
		self.cursor = None

	def connect(self):
		self.con = mysql.connector.connect(host=self.host, user=self.user,
																password=self.pw, database=self.db,
																allow_local_infile=True
		)
		self.cursor = self.con.cursor(named_tuple=True)

	def close(self):
		if self.con == None:
			return
		if self.cursor:
			self.cursor.close()
			self.cursor = None
		self.con.close()
		self.con = None

	def escape(self, s):
		return self.con.converter.escape(s)

	def query(self, q, params=None):
		#print(q)
		self.cursor.execute(q, params)

	def fetch_row(self):
		return self.cursor.fetchone()

	def fetch_all(self):
		res = []
		while True:
			r = self.fetch_row()
			if not r:
				break
			res.append(r)
		return res
