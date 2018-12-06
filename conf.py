import argparse
import json

ver=0
base=1200
max=1500
step_search = []
mtu_table=[[]]
notes = ""
DEFAULT_PROBE_TIMER = 15
CONFIRMATION_TIMER = 10
RAISE_TIMER = 60
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
parser.add_argument("--ptb", help="enable path too big", action="store_true")
parser.add_argument("--server-address4")
parser.add_argument("--server-port4", type=int)
parser.add_argument("--server-address6")
parser.add_argument("--server-port6", type=int)
parser.add_argument("-r","--real", help="Real link MTU", default="not set")
parser.add_argument("--rtt", help="Real trip time", default="not set")
parser.add_argument("--notes", help="Extra info about the experiment")
parser.add_argument("--bi", help="Enables a binary search experiment", action="store_true")
parser.add_argument("--state", help="Runs the full state machine with timers instead of different searches", action="store_true")


#commands with - are replaced with _ in the variable --server-port6 -> args.server_port6
args = parser.parse_args()
if args.config:
    with open(args.config) as f:
        j = json.load(f)
        if "base" in j:
            BASE_PMTU = j["base"]
        if "step" in j:
            step_search = j["step"]
        if "max" in j:
            MAX_PMTU = j["max"]
        if "table" in j:
            mtu_table = j["table"]
        if "max-probes" in j:
            MAX_PROBES = j["max-probes"]
        if "probe-timer" in j:
            DEFAULT_PROBE_TIMER = j["probe-timer"]

        if "server-address4" in j:
            server_address4 = j["server-address4"]
        if "server-port4" in j:
            server_port4 = j["server-port4"]
        if "server-address6" in j:
            server_address6 = j["server-address6"]
        if "server-port6" in j:
            server_port6 = j["server-port6"]
        if "notes" in j:
            notes = j["notes"]
         

if(not args.four and not args.six):
    print("Need to specify IPv4 or IPv6.")
    exit(-1)

if args.step:
    step_search = args.step
if args.base:
    BASE_PMTU = args.base
if args.max:
    MAX_PMTU = args.max
if args.table:
    mtu_table = args.table
if args.max_probes:
    MAX_PROBES = args.max_probes
if args.probe_timer:
    DEFAULT_PROBE_TIMER = args.probe_timer
if args.notes:
    notes = args.notes

if  args.server_address6:
    server_address6 = args.server_address6
    server_port6 = args.server_port6
if args.server_address4:
    server_address4 = args.server_address4
    server_port4 = args.server_port4
if args.four:
    server_address = server_address4
    server_port = server_port4
else:
    server_address = server_address6
    server_port = server_port6




    


