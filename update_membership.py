#! /usr/bin/python

from util import *
import sys
from db import DB

if len(sys.argv) < 2:
	fatal("Missing file name argument")

fname = sys.argv[1]
con = DB()
con.connect()
query = ("load data local infile '" + fname +
	"' replace into table member" +
	" fields terminated by ',' optionally enclosed by '\"'" +
	" ignore 1 lines (fname,lname,bdate,@gender,@email,usatf_no,@junk,@junk"
	+ ") set gender=substring(@gender,1,1)")
print(query)
con.query(query)
con.close()
