#!/bin/bash
cp results scripts/
cd scripts/
jq -c . < results > results_line &&
python parse_results.py &&
cat step1.csv step7.csv step9.csv table1.csv table2.csv| column -t -s, -n | tee results.tab |less -S
#cat step1.csv step7.csv step9.csv table1.csv table2.csv| column -t -s, -n >> results.tab
