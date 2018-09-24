#!/bin/bash

ssh root@192.168.2.100 ./all.sh ;
scp root@192.168.2.100:/root/results* ./ &&

./print_results.sh
