import os,sys

def get_config_var(var_name, def_val):
	return os.getenv(var_name, def_val)

def fatal(msg):
	sys.stderr.write("Error: " + msg + "\n")
	sys.exit(1)
