import socket
import sys
import json
import hashlib
import threading
import os
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
salt = "secret experiment salty boi"
tl = 5



parser = argparse.ArgumentParser(description="PLPMTUD experiment server")
parser.add_argument("--four", help="enable ipv4", action="store_true")
parser.add_argument("--six", help="enable ipv6", action="store_true")
parser.add_argument("-c", "--config")
parser.add_argument("--server-address4")
parser.add_argument("--server-port4", type=int)
parser.add_argument("--server-address6")
parser.add_argument("--server-port6", type=int)
parser.add_argument("-l", "--listen", type=int, default=tl)

args = parser.parse_args()
if args.config:
    with open(args.config) as f: 
        j = json.load(f)
    server_address4 = j["server-address4"]
    server_port4 = j["server-port4"]
    server_address6 = j["server-address6"]
    server_port6 = j["server-port6"]
    tl = j["listen"]
    salt = j["salt"]

if args.server_address4:
    server_address4 = args.server_address4
if args.server_port4:
    server_port4 = args.server_port4

if args.server_address6:
    server_address6 = args.server_address6
if args.server_port6:
    server_port6 = args.server_port6

tsock4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tsock4.bind((server_address4,server_port4))
tsock4.listen(tl) 

tsock6 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
tsock6.bind(("::1", 10006, 0,0))
#tsock6.bind((server_address6,server_port6,0,0))
tsock6.listen(tl) 

def handle_client_connection(client_socket):
        reply = client_socket.recv(1024)
        try:
            request = json.loads(reply)
            if request["type"] == "init":
                logging.info("Received init")
                hash = hashlib.sha1()
                hash.update(str(request["time"]))
                hash.update(request["addr"])
                hash.update(salt)
                request["token"] = hash.hexdigest() 
                client_socket.send(json.dumps(request))
            elif request["type"] == "fin":
                logging.info("Received fin")
                f=open("results", "a")
                f.write(reply)
                f.close()
        except:
            logging.warning("received not json")
	client_socket.close()
	logging.info("closed")

def run_http(tsock):
    while True:
        logging.info("waiting to accept")
	client_sock, address = tsock.accept()
	logging.info('Accepted connection from {}:{}'.format(address[0], address[1]))
	handle_client_connection(client_sock)
	logging.info("handled")

http_pid4 = os.fork()
if http_pid4 == 0:
    run_http(tsock4)
    exit()

http_pid6 = os.fork()
if http_pid6 == 0:
    run_http(tsock6)
    exit()

def confirm_token(token, addr, time):
    h = hashlib.sha1()
    h.update(str(time))
    h.update(addr)
    h.update(salt)
    
    return (token == h.hexdigest())
def udp_serve(sock):

    while True:
        logging.debug("waiting to receive probe")
        data, address = sock.recvfrom(65536)
        
        logging.debug("received %s bytes from %s" % (len(data), address))
        logging.debug(data)
        
        if not data:
            continue
        try:
            jsn = json.loads(data[:-32])
            if not confirm_token(jsn["token"],jsn["addr"],jsn["time"]):
                logging.warning("Token not confirmed")
                continue
            sent = sock.sendto("ack"+str(len(data))+"probe_received"+data[-32:], address)
            logging.debug("sent %s back to %s" % (str(len(data)), address))
        except:
            logging.warning("Bad probe")
usock4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
logging.info("starting up on %s " % server_address4)
usock4.bind((server_address4,server_port4))

usock6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
logging.info("starting up on %s " % server_address6)
#usock6.bind((server_address6, server_port6, 0,0))
usock6.bind(("::1", 10006, 0,0))


udp_pid4 = os.fork()
if udp_pid4 == 0:
    udp_serve(usock4)
    exit()

udp_pid6 = os.fork()
if udp_pid6 == 0:
    udp_serve(usock6)
    exit()

for id in [http_pid6,http_pid4, udp_pid4,udp_pid6]:
    os.waitpid(id,0)
