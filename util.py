import os,sys,re

BAD_CHARS_RE=re.compile(r"[^:\,_ \w]+")

def get_config_var(var_name, def_val):
	return os.getenv(var_name, def_val)

def fatal(msg):
	sys.stderr.write("Error: " + msg + "\n")
	sys.exit(1)

def usatf_age_expr():
	return "%s - year(bdate) - (date_format(bdate, %s) > %s) usatf_age"

def get_input(msg):
	return raw_input(msg)

def cleanup_str(s):
	return BAD_CHARS_RE.sub("", s.strip())
