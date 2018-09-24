ip route add 192.168.1.0/24 dev enp1s0
ip route add 192.168.3.0/24 dev enp3s0
ip -6 route add fc00::1/7 dev enp1s0
ip -6 route add fc00::3/7 dev enp3s0
