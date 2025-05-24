#! /usr/bin/python

from util import *
import sys
from db import DB

if len(sys.argv) < 2:
	fatal("Missing file name argument")

#fields = "(fname,lname,@bdate,@gender,@junk,usatf_no)"
fields = "(fname,@junk,lname,@bdate,@gender,usatf_no,@junk)"
#fields = "(@age, fname,lname,@bdate,@gender,@junk,usatf_no)"
#fields = "(@age,fname,@mi,lname,@suffix,@bdate,@gender,@phone,@email,usatf_no)"
date_fmt='%Y-%m-%d'
#date_fmt='%c/%d/%Y''

fname = sys.argv[1]
con = DB()
con.connect()
query = ("load data local infile '" + fname +
	"' replace into table member" +
	" fields terminated by ',' optionally enclosed by '\"'" +
	" ignore 1 lines " + fields
	+ " set gender=substring(@gender,1,1), bdate=str_to_date(@bdate, '" + date_fmt + "')")
print(query)
con.query(query)
con.close()
