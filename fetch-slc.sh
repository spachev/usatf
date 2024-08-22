#! /bin/bash

  unbuffer python fetch_sportstats.py --race-id=108762 | tee slc-track-15k-2020.txt 
  unbuffer python fetch_sportstats.py --race-id=108750 | tee slc-track-10k-2020.txt 
  unbuffer python fetch_sportstats.py --race-id=108722 | tee slc-track-5k-2020.txt 

