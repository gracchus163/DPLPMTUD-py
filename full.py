import socket
import sys
import IN
import uuid
import time
import json
from conf import *
import os
import scapy.all as scapy
import collections

def ptb_callback(pkt):
    icmU = pkt[scapy.ICMP][2]
    print("pr")
    if icmU.dport == server_port:
        #pkt[scapy.ICMP][2].show()
        print(icmU.len)
        print("OHAYUUUUUUUU")
        s = icmU[scapy.Raw].load
        if  token in s:
            print("PTB from our packet")
def ptb():
    scapy.sniff(filter="icmp[icmptype]=3 and icmp[icmpcode]=4", prn=ptb_callback)
def ptb6_callback(pkt):
    icmU = pkt[scapy.ICMPv6PacketTooBig][2]
    print("pr6")
    if icmU.dport == server_port:
        print(icmU.len)
        print("OHAYUUUUUUUU")
        s = icmU[scapy.Raw].load
        if  token in s:
            print("PTB6 from our packet")
def ptb6():
    scapy.sniff(filter="icmp6 and ip6[40] == 2",prn=ptb6_callback)

def SEARCH(step):
    print("additive search with step of "+str(step))
    probe_size=BASE_PMTU
    plpmtu=0
    count=0
    st = time.time()
    for probe_size in range(BASE_PMTU,(MAX_PMTU+1)-header_len, step):
        if(not send_probe(probe_size)):
            break
        plpmtu=probe_size
        count+=1
    return {"step":step, "plpmtu":plpmtu, "count":count, "time_taken":(time.time()-st), "est_rtt":PROBE_TIMER}


def SEARCH_table(table):
    print("table search start")
    plpmtu=0
    t =[int(i) for i in table]
    count=0
    st = time.time()
    for mtu in t:
        print(t)
        if mtu > MAX_PMTU-header_len:
            break
        print("table mtu of "+str(mtu))
        if(not send_probe(mtu)):
            break
        print("table updat PLPMTU to: "+str(mtu))
        plpmtu=mtu
        count+=1
    return {"table":table, "plpmtu":plpmtu, "count":count, "time_taken":(time.time()-st),"est_rtt":PROBE_TIMER}

			
def path_confirmation():
    if not send_probe(200):
        return False
    return send_probe(BASE_PMTU)

def smooth_rtt(n):
    weight = 0.4 # 0 <= weight < 1
    return (weight*PROBE_TIMER)+((1-weight)*n)

def send_probe(mtu):
    PROBE_COUNT=0
    global PROBE_TIMER
    sock.settimeout(PROBE_TIMER)
    tuple_msg = [
            ("token",token),
            ("time", timestamp),
            ("addr", server_address),
            ("version", ver),
            ("mtu", mtu),
            ("padding" , ""),
            ("real_rtt", real_rtt),
            ("probe_timer", PROBE_TIMER)]
    msg = collections.OrderedDict(tuple_msg)
            
    j_msg = json.dumps(msg)
    pad = mtu-len(j_msg)
    if pad < 0:
        print "pad less than 0, oops"
        pad = 0
    print(len(j_msg))
    print("mtu "+str(mtu)+"pad "+str(pad))
    msg["padding"] = "T"*pad
    j_msg = json.dumps(msg)

    while True:
        print("len j_msg: "+str(len(j_msg)))
        time_send = time.time()
        sock.sendto(j_msg, addr)
        print("sending probe of "+str(mtu))
        try:
                data, server = sock.recvfrom(MAX_PMTU)
                time_rtt = time.time() - time_send
                PROBE_TIMER = smooth_rtt(time_rtt)
                print("RTT: %f Probe_timer %f" % (time_rtt,PROBE_TIMER))
        except socket.timeout as err:
                PROBE_COUNT +=1
                print("probe timeout %d on MTU: %d with timer of %f" % (PROBE_COUNT, mtu, PROBE_TIMER))
    #            PROBE_TIMER = DEFAULT_PROBE_TIMER
     #           print("reset timer to %f" % (PROBE_TIMER))
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
            "probe_timer": PROBE_TIMER,
            "max_probes": MAX_PROBES,
            "res" : res,
            "real_mtu": args.real,
            "real_rtt": real_rtt,
            "ipv": ii
            }
    msg = json.dumps(data)
    client.send(msg)
    print("wrote results")
    client.close()


timestamp=time.time()
real_rtt=args.rtt

PROBE_TIMER = DEFAULT_PROBE_TIMER
if args.four:
    type_af = socket.AF_INET
    header_len=28
    ii = 4
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.IPPROTO_IP, IN.IP_MTU_DISCOVER, IN.IP_PMTUDISC_PROBE)
    addr = (server_address, server_port)
    token = init()
    ptb_pid = os.fork()
    if ptb_pid == 0:
        ptb()
        exit()
else:
    type_af = socket.AF_INET6
    header_len=48
    ii = 6
    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    sock.setsockopt(socket.IPPROTO_IPV6, IN.IPV6_MTU_DISCOVER, IN.IP_PMTUDISC_PROBE)
    addr = (server_address, server_port, 0,0)
    token = init()
    ptb_pid = os.fork()
    if ptb_pid == 0:
        ptb6()
        exit()


sock.settimeout(PROBE_TIMER)

if not path_confirmation():
    print "path confirmation failed"
    exit(-1)
results = {"step1":SEARCH(1)}
for s in step:
    PROBE_TIMER = DEFAULT_PROBE_TIMER
    results["step"+s] = SEARCH(int(s))
print(mtu_table)
i = 1
for t in mtu_table:
    PROBE_TIMER = DEFAULT_PROBE_TIMER
    results["table"+str(i)] = SEARCH_table(t)
    i += 1

send_results(results)
print >>sys.stderr, 'closing socket'
os.kill(ptb_pid, 9)
sock.close()

