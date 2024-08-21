import os,sys,re

BAD_CHARS_RE=re.compile(r"[^:\,\._ \w]+")

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
	try:
		s = "".join([c for c in s if ord(c) < 128])
		return BAD_CHARS_RE.sub("", s.encode('utf-8').strip())
	except:
		return ""

def time_to_ms(t):
	parts = str(t).split(':')
	res = 0
	for p in parts:
		res = res * 60.0 + float(p)
	return int(res * 1000)

def ms_to_time(t_ms):
	t_ms = int(t_ms)
	ms = t_ms % 60000
	ss = ms / 1000
	t_ms -= ms
	t_m = t_ms / 60000
	mm = t_m % 60
	hh = (t_m - mm) / 60
	return "{:02d}:{:02d}:{:02d}.{:03d}".format(hh, mm, ss, ms % 1000)
