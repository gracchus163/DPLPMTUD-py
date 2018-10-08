#!/bin/sh
head -n 1 step1.csv > step1_4.csv
head -n 1 step1.csv > step1_6.csv
head -n 1 step7.csv > step7_4.csv
head -n 1 step7.csv > step7_6.csv
head -n 1 step9.csv > step9_4.csv
head -n 1 step9.csv > step9_6.csv

grep ipv4 step1.csv >> step1_4.csv
grep ipv6 step1.csv >> step1_6.csv
grep ipv4 step7.csv >> step7_4.csv
grep ipv6 step7.csv >> step7_6.csv
grep ipv4 step9.csv >> step9_4.csv
grep ipv6 step9.csv >> step9_6.csv

head -n 1 table1.csv > table1_4.csv
head -n 1 table1.csv > table1_6.csv
head -n 1 table2.csv > table2_4.csv
head -n 1 table2.csv > table2_6.csv

grep ipv4 table1.csv >> table1_4.csv
grep ipv6 table1.csv >> table1_6.csv
grep ipv4 table2.csv >> table2_4.csv
grep ipv6 table2.csv >> table2_6.csv
