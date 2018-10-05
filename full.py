import socket
import sys
import IN
import uuid
import time
import json
from conf import *
import scapy.all as scapy
import collections
import thread

ptb_lock = thread.allocate_lock()
ptb_recv_mutex = False
ptb_val_mutex = 0
ptb_sport = 0
sport = 0

def ptb_callback(pkt):
    icmU = pkt[scapy.ICMP][2]
    print("ptb")
    if icmU.dport == server_port:
        #pkt[scapy.ICMP][2].show()
        print(icmU.len)
        s = icmU[scapy.Raw].load
        if  token in s:
            ptb_lock.acquire()
            global ptb_recv_mutex
            ptb_recv_mutex = True
            global ptb_val_mutex
            ptb_val_mutex = pkt[scapy.ICMP].nexthopmtu
            global ptb_sport
            ptb_sport = icmU.sport
            ptb_lock.release()
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
            ptb_lock.acquire()
            global ptb_recv_mutex
            ptb_recv_mutex = True
            global ptb_val_mutex
            ptb_val_mutex = pkt[scapy.ICMPv6PacketTooBig].mtu
            global ptb_sport
            ptb_sport = icmU.sport
            ptb_lock.release()
def ptb6():
    scapy.sniff(filter="icmp6 and ip6[40] == 2",prn=ptb6_callback)

def SEARCH(step):
    print("additive search with step of "+str(step))
    probe_size=BASE_PMTU
    plpmtu=0
    count=0
    st = time.time()
    for probe_size in range(BASE_PMTU,(MAX_PMTU+1)-header_len, step):
        reply, ptb_len = send_probe(probe_size, plpmtu)
        if(plpmtu == ptb_len-header_len):
            break
        if ptb_len-header_len > plpmtu:
            probe_size = ptb_len-header_len
            reply, ptb_len = send_probe(probe_size, plpmtu)
            if reply: #search complete
                plpmtu=probe_size
                count+=1
                break
            else:
                print "everything broken"
        if(not reply):
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
    for probe_size in t:
        print(t)
        if probe_size > MAX_PMTU-header_len:
            break
        print("table probe of "+str(probe_size))
        reply, ptb_len = send_probe(probe_size, plpmtu)
        if ptb_len-header_len == plpmtu:
            break
        if ptb_len-header_len > plpmtu:
            probe_size = ptb_len-header_len
            reply, ptb_len = send_probe(probe_size, plpmtu)
            if reply: #search complete
                plpmtu=probe_size
                count+=1
                break
            else:
                print "everything broken panic"
        if not reply:
            break
        print("table updat PLPMTU to: "+str(probe_size))
        plpmtu=probe_size
        count+=1
    return {"table":table, "plpmtu":plpmtu, "count":count, "time_taken":(time.time()-st),"est_rtt":PROBE_TIMER}

			
def path_confirmation():
    if not send_probe(300,300)[0]:
        return False
    return send_probe(BASE_PMTU, BASE_PMTU)[0]

def smooth_rtt(n):
    weight = 0.4 # 0 <= weight < 1
    return (weight*PROBE_TIMER)+((1-weight)*n)
    #return DEFAULT_PROBE_TIMER

def send_probe(probe_size,plpmtu):
    PROBE_COUNT=0
    global PROBE_TIMER
    sock.settimeout(PROBE_TIMER)
    tuple_msg = [
            ("token",token),
            ("time", timestamp),
            ("addr", server_address),
            ("version", ver),
            ("mtu", probe_size),
            ("padding" , ""),
            ("real_rtt", real_rtt),
            ("probe_timer", PROBE_TIMER)]
    msg = collections.OrderedDict(tuple_msg)
            
    j_msg = json.dumps(msg)
    pad = probe_size-len(j_msg)-32 #length of packet uuid
    if pad < 0:
        print "pad less than 0, oops"
        pad = 0
    print(len(j_msg))
    print("probe_size "+str(probe_size)+"pad "+str(pad))
    msg["padding"] = "T"*pad
    j_msg = json.dumps(msg)
    sport = sock.getsockname()[1]
    while True:
        u = uuid.uuid4()
        print("len j_msg: "+str(len(j_msg)))
        
        if args.ptb:
            ptb_len = -1
            ptb_lock.acquire()
            print("locked")
            global ptb_recv_mutex
            global ptb_sport
            print("sport %d ptb_sport %d" % (sport, ptb_sport))
            if (ptb_recv_mutex and  ptb_sport==sport):
                ptb_recv_mutex = False
                ptb_len = ptb_val_mutex
                ptb_lock.release()
                print("PTB from our packet with len: %d"%(ptb_len))
                return (False, ptb_len)    #search complete
            ptb_lock.release()

        time_send = time.time()
        sock.sendto(j_msg+u.hex, addr)
        sport = sock.getsockname()[1]
        print("sending probe of "+str(len(j_msg+u.hex)))
        timeout = time.time()+PROBE_TIMER
        while time.time() < timeout:
            try:
                data, server = sock.recvfrom(MAX_PMTU)
            except:
                break
            print data
            print u.hex
            if u.hex not in data:
                continue
            time_rtt = time.time() - time_send
            PROBE_TIMER = smooth_rtt(time_rtt)
            print("RTT: %f Probe_timer %f" % (time_rtt,PROBE_TIMER))
            return (True,-1)
        PROBE_COUNT +=1
        print("probe timeout %d on probe_size: %d with timer of %f" % (PROBE_COUNT, probe_size, PROBE_TIMER))
#            PROBE_TIMER = DEFAULT_PROBE_TIMER
#           print("reset timer to %f" % (PROBE_TIMER))
        if PROBE_COUNT >= MAX_PROBES:
            PROBE_COUNT=0
            return (False,-1)
        continue

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
    opt = (socket.IPPROTO_IP, IN.IP_MTU_DISCOVER, IN.IP_PMTUDISC_PROBE)
    header_len=28
    ii = 4
    addr = (server_address, server_port)
    token = init()
    if args.ptb:
        thread.start_new_thread(ptb, ())
else:
    type_af = socket.AF_INET6
    opt = (socket.IPPROTO_IPV6, IN.IPV6_MTU_DISCOVER, IN.IP_PMTUDISC_PROBE)
    header_len=48
    ii = 6
    addr = (server_address, server_port, 0,0)
    token = init()
    if args.ptb:
        thread.start_new_thread(ptb6, ())



sock = socket.socket(type_af, socket.SOCK_DGRAM)
sock.setsockopt(opt[0],opt[1],opt[2])
print sock.getsockname()
sport = sock.getsockname()[1]
if not path_confirmation():
    print "path confirmation failed"
    #send_results("Path confirmation failed")
    exit(-1)
sock = socket.socket(type_af, socket.SOCK_DGRAM)
sock.setsockopt(opt[0],opt[1],opt[2])
sport = sock.getsockname()[1]
results = {"step1":SEARCH(1)}
for s in step:
    PROBE_TIMER = DEFAULT_PROBE_TIMER
    sock = socket.socket(type_af, socket.SOCK_DGRAM)
    sock.setsockopt(opt[0],opt[1],opt[2])
    sport = sock.getsockname()[1]

    results["step"+s] = SEARCH(int(s))
print(mtu_table)
i = 1
for t in mtu_table:
    PROBE_TIMER = DEFAULT_PROBE_TIMER
    sock = socket.socket(type_af, socket.SOCK_DGRAM)
    sock.setsockopt(opt[0],opt[1],opt[2])
    sport = sock.getsockname()[1]
    results["table"+str(i)] = SEARCH_table(t)
    i += 1

send_results(results)
print >>sys.stderr, 'closing socket'
sock.close()

