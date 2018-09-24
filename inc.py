import socket
import sys
import uuid
import time

PROBE_TIMER=15
PMTU_RAISE_TIMER=600
CONFIRMATION_TIMER=3

MAX_PROBES=10
MAX_PMTU=1500	#Max the local link can support
BASE_PMTU=1200

PROBED_SIZE=BASE_PMTU #CUrrent probe size
PLPMTU=BASE_PMTU	  #Current application siz


def SEARCH():
        global PLPMTU
        global PROBED_SIZE
        PROBED_SIZE=PLPMTU
        print("start search PLPMTU="+str(PLPMTU))
	while True:
		if(send_probe(PROBED_SIZE)):
			PLPMTU=PROBED_SIZE #MTU confirmed so update
                        print("update PLPMTU to:"+str(PLPMTU))
                        if PLPMTU >= MAX_PMTU-36:
                            return
			PROBED_SIZE+=step #received probe so increment probe MTU
		else:
			return

			
			
def send_probe(mtu):
        PROBE_COUNT=0
	while True:
		message = token+("T"*mtu)
		sock.sendto(message, server_address)
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

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#generate session token
token = str(uuid.uuid4())

step=10
server_address = ('localhost', 15000)


#	path-confirmation

sock.settimeout(PROBE_TIMER)
SEARCH()

raise_timer = time.time()
conf_timer = time.time()
while True:
    if time.time()-raise_timer > PMTU_RAISE_TIMER:
        print("raise timer")
	sock.settimeout(PROBE_TIMER)
        SEARCH()
        raise_timer = time.time()
    if time.time()-conf_timer > CONFIRMATION_TIMER:
        print("confirmation timer")
        sock.settimeout(CONFIRMATION_TIMER)
        if(not send_probe(PROBED_SIZE)):
            PLPMTU=BASE_PMTU
            #path-confirmation
            SEARCH()
            PLPMTU=BASE_PMTU
        conf_timer = time.time()
                            
print >>sys.stderr, 'closing socket'
sock.close()
			
