import csv
import json
import sys

data = []
ver = 0
with open("results_line") as f:
    for l in f:
        j = json.loads(l)
        if j["version"] == ver:
            data.append(j)

results = { "addr": [],
            "time": [],
            "real": [],
            "real_count":[],
            "real_time":[],
            "step7":[],
            "step7_count":[],
            "step7_time":[],
            "step9":[],
            "step9_count":[],
            "step9_time":[],
            "table1":[],
            "table1_time":[],
            "table1_count":[],
            "table2":[],
            "table2_time":[],
            "table2_count":[],
            }
step1 = {"Real link size":[],
        "Estimated round trip time":[],
        "Real round trip time":[],
        "Step Size":[],
        "MTU found":[],
        "Time to complete":[],
        "Number of probes received":[],
        "IPv":[]
        }
step7 = {"Real link size":[],
        "Estimated round trip time":[],
        "Real round trip time":[],
        "Step Size":[],
        "MTU found":[],
        "Time to complete":[],
        "Number of probes received":[],
        "IPv":[]
        }
step9 = {"Real link size":[],
        "Estimated round trip time":[],
        "Real round trip time":[],
        "Step Size":[],
        "MTU found":[],
        "Time to complete":[],
        "Number of probes received":[],
        "IPv":[]
        }
table1 = {"Real link size":[],
        "Estimated round trip time":[],
        "Real round trip time":[],
        "Table values":[],
        "MTU found":[],
        "Time to complete":[],
        "Number of probes received":[],
        "IPv":[]
        }
table2 = {"Real link size":[],
        "Estimated round trip time":[],
        "Real round trip time":[],
        "Table values":[],
        "MTU found":[],
        "Time to complete":[],
        "Number of probes received":[],
        "IPv":[]
        }
for i in data: 
    results["addr"].append(str(i["addr"][0]))
    results["time"].append(i["time"])
    r = i["res"]
    real_link = i["real_mtu"]
    real_rtt = i["real_rtt"]
    est_rtt = "{0:.4f}".format(i["probe_timer"])
    ii = "ipv"+str(i["ipv"])
    step1["Real link size"].append(real_link)  
    step7["Real link size"].append(real_link)  
    step9["Real link size"].append(real_link)  
    table1["Real link size"].append(real_link)  
    table2["Real link size"].append(real_link)  
    step1["IPv"].append(ii)  
    step7["IPv"].append(ii)  
    step9["IPv"].append(ii)  
    table1["IPv"].append(ii)  
    table2["IPv"].append(ii)  
    step1["Real round trip time"].append(real_rtt)  
    step7["Real round trip time"].append(real_rtt)  
    step9["Real round trip time"].append(real_rtt)  
    table1["Real round trip time"].append(real_rtt)  
    table2["Real round trip time"].append(real_rtt)  
    step1["Estimated round trip time"].append("{0:.4f}".format(1000*r["step1"]["est_rtt"]))
    step7["Estimated round trip time"].append("{0:.4f}".format(1000*r["step7"]["est_rtt"]))
    step9["Estimated round trip time"].append("{0:.4f}".format(1000*r["step9"]["est_rtt"]))
    table1["Estimated round trip time"].append("{0:.4f}".format(1000*r["table1"]["est_rtt"]))
    table2["Estimated round trip time"].append("{0:.4f}".format(1000*r["table2"]["est_rtt"]))

    step1["Step Size"].append(1)  
    step7["Step Size"].append(7)  
    step9["Step Size"].append(9)  
    table1["Table values"].append("1300 1350")  
    table2["Table values"].append("1250 1260 1270 1280")
    step1["MTU found"].append(r["step1"]["plpmtu"])  
    step7["MTU found"].append(r["step7"]["plpmtu"])  
    step9["MTU found"].append(r["step9"]["plpmtu"])  
    table1["MTU found"].append(r["table1"]["plpmtu"])  
    table2["MTU found"].append(r["table2"]["plpmtu"])  
    step1["Time to complete"].append("{0:.4f}".format(r["step1"]["time_taken"]))
    step7["Time to complete"].append("{0:.4f}".format(r["step7"]["time_taken"]))
    step9["Time to complete"].append("{0:.4f}".format(r["step9"]["time_taken"]))
    table1["Time to complete"].append("{0:.4f}".format(r["table1"]["time_taken"]))
    table2["Time to complete"].append("{0:.4f}".format(r["table2"]["time_taken"]))
    step1["Number of probes received"].append(r["step1"]["count"])
    step7["Number of probes received"].append(r["step7"]["count"])
    step9["Number of probes received"].append(r["step9"]["count"])
    table1["Number of probes received"].append(r["table1"]["count"])
    table2["Number of probes received"].append(r["table2"]["count"])
with open("step1.csv", "wb") as f:
   writer = csv.writer(f)
   writer.writerow(step1.keys())
   writer.writerows(zip(*step1.values()))
with open("step7.csv", "wb") as f:
   writer = csv.writer(f)
   writer.writerow(step7.keys())
   writer.writerows(zip(*step7.values()))
with open("step9.csv", "wb") as f:
   writer = csv.writer(f)
   writer.writerow(step9.keys())
   writer.writerows(zip(*step9.values()))
with open("table1.csv", "wb") as f:
   writer = csv.writer(f)
   writer.writerow(table1.keys())
   writer.writerows(zip(*table1.values()))
with open("table2.csv", "wb") as f:
   writer = csv.writer(f)
   writer.writerow(table2.keys())
   writer.writerows(zip(*table2.values()))
