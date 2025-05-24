#! /bin/bash

# python2 upload_race.py --file ogden-5k-2023.txt --delim ";" --race-name "Ogden Winter Series 5K"  --race-date 2023-02-18 --race-dist-cm 500000
# python2 upload_race.py --file ogden-10k-2023.txt --delim ";" --race-name "Ogden Winter Series 10K"  --race-date 2023-03-04 --race-dist-cm 1000000

#python2 upload_race.py --file ogden-10m-2023.txt --delim ";" --race-name "Ogden Winter Series 10 Miles"  --race-date 2023-03-04 --race-dist-cm 1609340

#python2 upload_race.py --file may-4th-5k-2023.txt --delim ";" --race-name "May The 4th 5K"  --race-date 2023-05-06 --race-dist-cm 500000
#python2 upload_race.py --file slctrack-5k-2023.txt --delim ";" --race-name "SLC Track 5K"  --race-date 2023-05-27 --race-dist-cm 500000
#python2 upload_race.py --file slctrack-10k-2023.txt --delim ";" --race-name "SLC Track 10K"  --race-date 2023-06-10 --race-dist-cm 1000000
#python2 upload_race.py --file slctrack-15k-2023.txt --delim ";" --race-name "SLC Track 15K"  --race-date 2023-06-24 --race-dist-cm 1500000
#python2 upload_race.py --file steel-days-10k-2023.txt --delim ";" --race-name "American Fork Steel Days 10K"  --race-date 2023-07-22 --race-dist-cm 1000000
#python2 upload_race.py --file tou-half-2023.txt --delim ";" --race-name "Top of Utah Half Marathon"  --race-date 2023-08-26 --race-dist-cm 2109750
#python2 upload_race.py --force-manual-match --file tou-mar-2023.txt --delim ";" --race-name "Top of Utah Marathon"  --race-date 2023-09-16 --race-dist-cm 4219500

set -x -e
python2 upload_race.py --file slc-track-5k-2025.csv --delim "," --race-name "SLC Track 5K"  --race-date 2025-01-25 --race-dist-cm 500000
python2 upload_race.py --file slc-track-10k-2025.csv --delim "," --race-name "SLC Track 10K"  --race-date 2025-02-08 --race-dist-cm 1000000
python2 upload_race.py --file slc-track-15k-2025.csv --delim "," --race-name "SLC Track 15K"  --race-date 2025-02-22 --race-dist-cm 1500000

python2 upload_race.py --file eggs-legs-5k-2025.csv --delim "," --race-name "Eggs Legs 5K"  --race-date 2025-04-19 --race-dist-cm 500000
#python2 upload_race.py --file uvm-2024.txt --delim ";" --race-name "Utah Valley Half Marathon"  --race-date 2024-06-01 --race-dist-cm 2109750
#python2 upload_race.py --file ogden-10m-2024.txt --delim ";" --race-name "Ogden Winter Series 10 Miles"  --race-date 2024-03-16 --race-dist-cm 1609340
#python2 upload_race.py --file tou-half-2024.txt --delim ";" --race-name "Top of Utah Half Marathon"  --race-date 2024-08-24 --race-dist-cm 2109750
#python2 upload_race.py --force-manual-match --file tou-mar-2024.txt --delim ";" --race-name "Top of Utah Marathon"  --race-date 2024-09-21 --race-dist-cm 4219500

#python2 upload_race.py --force-manual-match --auto-single-match --file xc-2024.txt --delim ";" --race-name "USATF XC Championship" --race-date 2024-11-09 --race-dist-cm 500000
python2 score_circuit.py > test.html

