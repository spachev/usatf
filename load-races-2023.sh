#! /bin/bash

# python2 upload_race.py --file ogden-5k-2023.txt --delim ";" --race-name "Ogden Winter Series 5K"  --race-date 2023-02-18 --race-dist-cm 500000
# python2 upload_race.py --file ogden-10k-2023.txt --delim ";" --race-name "Ogden Winter Series 10K"  --race-date 2023-03-04 --race-dist-cm 1000000

#python2 upload_race.py --file ogden-10m-2023.txt --delim ";" --race-name "Ogden Winter Series 10 Miles"  --race-date 2023-03-04 --race-dist-cm 1609340

#python2 upload_race.py --file may-4th-5k-2023.txt --delim ";" --race-name "May The 4th 5K"  --race-date 2023-05-06 --race-dist-cm 500000
#python2 upload_race.py --file slctrack-5k-2023.txt --delim ";" --race-name "SLC Track 5K"  --race-date 2023-05-27 --race-dist-cm 500000
#python2 upload_race.py --file slctrack-10k-2023.txt --delim ";" --race-name "SLC Track 10K"  --race-date 2023-06-10 --race-dist-cm 1000000
#python2 upload_race.py --file slctrack-15k-2023.txt --delim ";" --race-name "SLC Track 15K"  --race-date 2023-06-24 --race-dist-cm 1500000
#python2 upload_race.py --file uvm-2023.txt --delim ";" --race-name "Utah Valley Half Marathon"  --race-date 2023-06-03 --race-dist-cm 2109750
#python2 upload_race.py --file steel-days-10k-2023.txt --delim ";" --race-name "American Fork Steel Days 10K"  --race-date 2023-07-22 --race-dist-cm 1000000
#python2 upload_race.py --file tou-half-2023.txt --delim ";" --race-name "Top of Utah Half Marathon"  --race-date 2023-08-26 --race-dist-cm 2109750
python2 upload_race.py --force-manual-match --file tou-mar-2023.txt --delim ";" --race-name "Top of Utah Marathon"  --race-date 2023-09-16 --race-dist-cm 4219500
python2 score_circuit.py > test.html

