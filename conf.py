import argparse
import json

ver=0
base=1200
max=1500
mtu_table=[["1300","1350"]]
probe_timer=1
max_probes=10
# Command line options overwrite config options

parser = argparse.ArgumentParser(description="PLPMTUD experiment")
parser.add_argument("-b", "--base", help="base PMTU", type=int)
parser.add_argument("-m", "--max", help="max PMTU", type=int)
parser.add_argument("-s", "--step", help="step size for additive search", action="append")
parser.add_argument("-t", "--table", help="table values", nargs="+", action="append")
parser.add_argument("--probe-timer",help="timeout for probes sent", type=int)
parser.add_argument("--max-probes",help="maximum probes to send before calling it a day", type=int)
parser.add_argument("-c", "--config", help="json file containing configuration options")
parser.add_argument("--four", help="enable ipv4", action="store_true")
parser.add_argument("--six", help="enable ipv6", action="store_true")
parser.add_argument("--server-address4")
parser.add_argument("--server-port4", type=int)
parser.add_argument("--server-address6")
parser.add_argument("--server-port6", type=int)

#commands with - are replaced with _ in the variable --server-port6 -> args.server_port6
args = parser.parse_args()
if args.config:
    with open(args.config) as f:
        j = json.load(f)
        BASE_PMTU = j["base"]
        step = j["step"]
        MAX_PMTU = j["max"]
        mtu_table = j["table"]
        MAX_PROBES = j["max-probes"]
        PROBE_TIMER = j["probe-timer"]

        if j["four"]:
            server_address = j["server-address4"]
            server_port = j["server-port4"]
        if j["six"]:
            server_address = j["server-address6"]
            server_port = j["server-port6"]

if(not args.four and not args.six):
    print("Need to specify IPv4 or IPv6.")
    exit(-1)

if args.step:
    step = args.step
if args.base:
    BASE_PMTU = args.base
if args.max:
    MAX_PMTU = args.max
if args.table:
    mtu_table = args.table
if args.max_probes:
    MAX_PROBES = args.max_probes
if args.probe_timer:
    PROBE_TIMER = args.probe_timer

if  args.six and args.server_address6:
    server_address = args.server_address6
    server_port = args.server_port6
elif args.four and args.server_address4:
    server_address = args.server_address4
    server_port = args.server_port4
    




    


