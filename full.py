import socket
import sys
import IN
import uuid
import time
import json
from conf import *


def SEARCH(step):
    print("additive search with step of "+str(step))
    probe_size=BASE_PMTU
    plpmtu=0
    for probe_size in range(BASE_PMTU,MAX_PMTU+1, step):
        if(not send_probe(probe_size)):
            break
        plpmtu=probe_size
    return ("step search", step, plpmtu)


def SEARCH_table(table):
    print("table search start")
    plpmtu=0
    t =[int(i) for i in table]
    for mtu in t:
        print(t)
        if mtu > MAX_PMTU:
            break
        print("table mtu of "+str(mtu))
        if(not send_probe(mtu)):
            break
        print("table updat PLPMTU to: "+str(mtu))
        plpmtu=mtu
    return ("table search", table, plpmtu)

			
			
def send_probe(mtu):
    PROBE_COUNT=0
    msg = {
            "token":token,
            "time": timestamp,
            "addr": server_address,
            "version": ver,
            "mtu": mtu,
            "padding" : ""
            }
    j_msg = json.dumps(msg)
    pad = mtu-len(j_msg)-header_len
    print("mtu "+str(mtu)+"pad "+str(pad))
    msg["padding"] = "T"*pad
    j_msg = json.dumps(msg)

    while True:
        print("len j_msg: "+str(len(j_msg)))
        sock.sendto(j_msg, addr)
        print("sending probe of "+str(mtu))
        try:
                data, server = sock.recvfrom(MAX_PMTU)
        except socket.timeout as err:
                PROBE_COUNT +=1
                print("probe timeout %d on MTU: %d" % (PROBE_COUNT, mtu))
                if PROBE_COUNT >= MAX_PROBES:
                        PROBE_COUNT=0
                        return False
                continue
        else:
            return True
def init():
    data = {
            "type" : "init",
            "time" : timestamp,
            "version" : ver,
            "token" : "hi",
            "addr" : server_address
            }
    init_json = json.dumps(data)
    client = socket.socket(type_af, socket.SOCK_STREAM)
    print(addr)
    client.connect(addr)
    client.send(init_json)

    resp = json.loads(client.recv(4096))
    print resp
    
    client.close()

    return resp["token"]


def send_results(res):
    client = socket.socket(type_af, socket.SOCK_STREAM)
    client.connect(addr)
    data = {
            "type": "fin",
            "time": timestamp,
            "version": ver,
            "token" : token,
            "addr" : addr,
            "res" : res
            }
    msg = json.dumps(data)
    client.send(msg)
    print("wrote results")
    client.close()


timestamp=time.time()

if args.four:
    type_af = socket.AF_INET
    header_len=28
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.IPPROTO_IP, IN.IP_MTU_DISCOVER, IN.IP_PMTUDISC_PROBE)
    addr = (server_address, server_port)
    token = init()
else:
    type_af = socket.AF_INET6
    header_len=48
    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    sock.setsockopt(socket.IPPROTO_IPV6, IN.IPV6_MTU_DISCOVER, IN.IP_PMTUDISC_PROBE)
    addr = (server_address, server_port, 0,0)
    token = init()

sock.settimeout(PROBE_TIMER)
results = []
results.append(SEARCH(1))
for s in step:
    results.append(SEARCH(int(s)))
print(mtu_table)
for t in mtu_table:
    results.append(SEARCH_table(t))

send_results(results)
print >>sys.stderr, 'closing socket'
sock.close()

