#!/bin/bash

ssh root@192.168.1.1 tcpdump not port 22 -w results.pcap &
ssh user@192.168.1.1 python MTUD/full_server.py -c MTUD/server_conf.json &> /dev/null &

