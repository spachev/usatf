#! /bin/bash

# Mark Jesse Cook with !0 to avoid the match with Riley Cook
# python2 scrape_brooksee.py --param-id=167742 --url-part=wr5 --race-id=166945 --event=5K > ogden-5k-2023.txt
# python2 scrape_brooksee.py --param-id=167744 --url-part=w10 --race-id=166944 --event=10K > ogden-10k-2023.txt
#python2 scrape_brooksee.py --param-id=167746 --url-part=wrt --race-id=166947 --event="10 Mile - (9.7 mi)" > ogden-10m-2023.txt
#python2 scrape_webscorer.py --race-id=313914 > may-4th-5k-2023.txt
#python2 scrape_webscorer.py --race-id=316227 --did=388198 > slctrack-5k-2023.txt
#python2 scrape_webscorer.py --race-id=317919 --did=390904 > slctrack-10k-2023.txt
#python2 scrape_webscorer.py --race-id=319339 --did=393437 > slctrack-15k-2023.txt
#python2 scrape_runsum.py --race-id=568 --event="Half Marathon" > uvm-2023.txt
#python2 scrape_runsignup.py --race-id=36741 --result-set-id=393823 > steel-days-10k-2023.txt
#python2 scrape_brooksee.py --param-id=168547 --url-part=tuh --race-id=167041 --event="Half Marathon" > tou-half-2023.txt
python2 scrape_runner_card.py > tou-mar-2023.txt
