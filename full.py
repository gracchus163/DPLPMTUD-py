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
import logging

logging.basicConfig(level=logging.DEBUG, format='%(message)s')

ptb_lock = thread.allocate_lock()
ptb_recv_mutex = False
ptb_val_mutex = 0
ptb_sport = 0
est_rtt = 0.0

def ptb_callback(pkt):
    icmU = pkt[scapy.ICMP][2]
    logging.debug("PTB4 received")
    if icmU.dport == server_port:
        #pkt[scapy.ICMP][2].show()
        sca = icmU[scapy.Raw].load
        if  token in sca:
            logging.debug("PTB token confirmed")
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
    logging.debug("PTB6 received")
    if icmU.dport == server_port:
        sca = icmU[scapy.Raw].load
        if  token in sca:
            logging.debug("PTB6 token confirmed")
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
    logging.debug("additive search with step of "+str(step))
    probe_size=BASE_PMTU
    plpmtu=BASE_PMTU
    count=0
    extra = ""
    if args.ptb:
        extra += "PTBEN"
    st = time.time()
    for probe_size in range(BASE_PMTU,(MAX_PMTU+1)-header_len, step):
        reply, ptb_len = send_probe(probe_size, plpmtu)
        if(plpmtu == ptb_len-header_len):
            extra += "PTBEQ"
            break
        if ptb_len-header_len > plpmtu:
            probe_size = ptb_len-header_len
            reply, ptb_len = send_probe(probe_size, plpmtu)
            if reply: #search complete
                plpmtu=probe_size
                count+=1
                extra += "PTBSR"
                break
            else:
                extra += "PTBERR"
                logging.error("Could not send probe of size PTB %d" %(ptb_len))
        if ptb_len-header_len < plpmtu and not ptb_len == -1 :
            logging.error("PTB %d smaller than plpmtu %d" %(ptb_len, plpmtu))
        if(not reply):
            break

        plpmtu=probe_size
        count+=1
    return {"step":step, "plpmtu":plpmtu, "count":count, "time_taken":(time.time()-st), "est_rtt":est_rtt, "notes":extra}


def SEARCH_table(table):
    logging.debug("table search start")
    plpmtu=BASE_PMTU    #path confirmation completed so base works
    t_list=[int(i) for i in table]
    count=0
    st = time.time()
    extra = ""
    if args.ptb:
        extra += "PTBEN"
    for probe_size in t_list:
        logging.debug("table values: "+str(t_list))
        if probe_size > MAX_PMTU-header_len:
            extra += "MAXOF"    #max overflow
            break
        logging.debug("table probe of "+str(probe_size))
        reply, ptb_len = send_probe(probe_size, plpmtu)
        if ptb_len-header_len == plpmtu:
            extra+= "PTBEQ"     #PTB received and equal to plpmtu
            break
        if ptb_len-header_len > plpmtu:
            probe_size = ptb_len-header_len
            reply, ptb_len = send_probe(probe_size, plpmtu)
            if reply: #search complete
                plpmtu=probe_size
                count+=1
                extra += "PTBSR"    #PTB received and confirmed
                break
            else:
                extra += "PTBERR"
                logging.error("Could not send probe of size PTB %d" %(ptb_len))
        if ptb_len-header_len < plpmtu and not ptb_len == -1 :
            logging.error("PTB %d smaller than plpmtu %d" %(ptb_len, plpmtu))
        if not reply:
            break
        logging.debug("table updat PLPMTU to: "+str(probe_size))
        plpmtu=probe_size
        count+=1
    return {"table":table, "plpmtu":plpmtu, "count":count, "time_taken":(time.time()-st),"est_rtt":est_rtt, "notes":extra}

			
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
        logging.warning( "pad less than 0, oops")
        pad = 0
    logging.debug("probe_size "+str(probe_size)+"pad "+str(pad))
    msg["padding"] = "T"*pad
    j_msg = json.dumps(msg)
    sport = sock.getsockname()[1]
    window = []
    sent_times = []
    while True:
        u = uuid.uuid4()
        window.append(u)
        logging.debug("len j_msg: "+str(len(j_msg)))
        
        if args.ptb:
            ptb_len = -1
            ptb_lock.acquire()
            global ptb_recv_mutex
            global ptb_sport
            logging.debug("sport %d ptb_sport %d" % (sport, ptb_sport))
            if (ptb_recv_mutex and  ptb_sport==sport):
                ptb_recv_mutex = False
                ptb_len = ptb_val_mutex
                ptb_lock.release()
                logging.info("PTB from our packet with len: %d"%(ptb_len))
                return (False, ptb_len)    #search complete
            ptb_lock.release()

        sock.settimeout(PROBE_TIMER)
        time_send = time.time()
        sent_times.append(time_send)

        sock.sendto(j_msg+u.hex, addr)
        sport = sock.getsockname()[1]
        logging.info("sending probe of "+str(len(j_msg+u.hex)))
        timeout = time.time()+PROBE_TIMER
        logging.debug("sent: "+u.hex)
        while time.time() <= timeout:
            try:
                logging.debug("waiting to recv")
                data, server = sock.recvfrom(MAX_PMTU)
            except:
                logging.info("timeout break")
                break
            logging.info("data received"+ data)
            #for w, t in zip(window, sent_times):
            #    if w.hex in data:
            #        time_rtt = time.time() - t
            #        PROBE_TIMER = smooth_rtt(time_rtt)
            #        global est_rtt
            #        est_rtt = PROBE_TIMER
            #        logging.debug("RTT: %f Probe_timer %f" % (time_rtt,PROBE_TIMER))
            #        return (True,-1)
            #        break
            #continue #window.hex not in data
            #prev behaviour
            if u.hex not in data:
                print("wrong hex")
                continue
            time_rtt = time.time() - time_send
            PROBE_TIMER = smooth_rtt(time_rtt)
            global est_rtt
            est_rtt = PROBE_TIMER
            logging.debug("RTT: %f Probe_timer %f" % (time_rtt,PROBE_TIMER))
            return (True,-1)
        PROBE_COUNT +=1
        logging.info("probe timeout %d on probe_size: %d with timer of %f" % (PROBE_COUNT, probe_size, PROBE_TIMER))
#        PROBE_TIMER = smooth_rtt(DEFAULT_PROBE_TIMER)       #somewhat hacky to fix consistent late timeouts. I think the probetimer should be modified on timeout, how to?
        if (PROBE_COUNT%3)==0 :
            PROBE_TIMER *= 2
        logging.info("upped timer to %f" % (PROBE_TIMER))
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
    logging.info("Connecting to "+str(addr))
    client.connect(addr)
    client.send(init_json)

    resp = json.loads(client.recv(4096))
    logging.debug("Init response "+ str(resp)) 
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
            "ipv": ii,
            "notes": notes
            }
    msg = json.dumps(data)
    client.send(msg)
    logging.info("sent results")
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
logging.debug("socket name: "+str(sock.getsockname()))
if not path_confirmation():
    logging.error("path confirmation failed")
    #send_results("Path confirmation failed")
    exit(-1)
sock = socket.socket(type_af, socket.SOCK_DGRAM)
sock.setsockopt(opt[0],opt[1],opt[2])
results = {"step1":SEARCH(1)}
for s in step_search:
    PROBE_TIMER = DEFAULT_PROBE_TIMER
    sock = socket.socket(type_af, socket.SOCK_DGRAM)
    sock.setsockopt(opt[0],opt[1],opt[2])

    results["step"+s] = SEARCH(int(s))
num_tables = 1
for t in mtu_table:
    if not t:
        break
    PROBE_TIMER = DEFAULT_PROBE_TIMER
    sock = socket.socket(type_af, socket.SOCK_DGRAM)
    sock.setsockopt(opt[0],opt[1],opt[2])
    results["table"+str(num_tables)] = SEARCH_table(t)
    num_tables += 1

send_results(results)
sock.close()

