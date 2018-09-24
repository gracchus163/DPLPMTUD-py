#!/bin/bash


ip link set enp1s0 mtu 1300 &&
ssh user@192.168.3.1 ./exp.sh &> /dev/null &&

ip link set enp1s0 mtu 1400 &&
ssh user@192.168.3.1 ./exp.sh &> /dev/null &&

ip link set enp1s0 mtu 1500 &&
ssh user@192.168.3.1 ./exp.sh  &> /dev/null &&

echo done
