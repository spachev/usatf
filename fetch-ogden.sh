#! /bin/bash

# This does not work

LAST_PAGE_START=1001
PAGE_SIZE=100
BASE_URL="https://www.runraceresults.com/Secure/raceResultsAPI.cfm?do=race%3Aresults%3Aoneclick&EVID=RCQW2018&RCID=1&TYPE=overall"

for ((i=1; i <= LAST_PAGE_START; i += PAGE_SIZE))
do
	url=$BASE_URL"&SROW=$i"
	curl -s $url | html2text -width 500 | tail -n +4 | \

#		awk -F '[[:space:]][[:space:]]+' \
#		'BEGIN { OFS = ";" }{ split($4,a," "); print $1,$2,a[2]}'
done
