tshark -r results.pcap -Y "ip.dst == 192.168.1.1  and not (tcp.port==22) and ip.src == 192.168.3.1" -Tfields -e ip.len -e ip.src
