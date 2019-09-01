#! /usr/bin/python

from util import *
import sys
from db import DB

if len(sys.argv) < 2:
	fatal("Missing file name argument")

fname = sys.argv[1]
con = DB()
con.connect()
con.query("load data local infile '" + fname +
	"' replace into table member" +
	" fields terminated by ',' optionally enclosed by '\"'" +
	" ignore 1 lines (usatf_no,fname,mname,lname,name_suffix," 
	+ "city,gender,@bdate_str)" +
	" set bdate = str_to_date(@bdate_str, '%Y/%m/%d')"
)
con.close()
