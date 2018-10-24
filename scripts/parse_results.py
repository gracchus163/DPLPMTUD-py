import csv
import json
import sys
import time

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
step1 = {"Configured link size":[],
        "Estimated round trip time":[],
        "Configured round trip time":[],
        "Step Size":[],
        "MPS found":[],
        "Time to complete":[],
        "Number of probes received":[],
        "Notes":[],
        "Start Time":[],
        "IPv":[]
        }
step7 = {"Configured link size":[],
        "Estimated round trip time":[],
        "Configured round trip time":[],
        "Step Size":[],
        "MPS found":[],
        "Time to complete":[],
        "Number of probes received":[],
        "Notes":[],
        "Start Time":[],
        "IPv":[]
        }
step9 = {"Configured link size":[],
        "Estimated round trip time":[],
        "Configured round trip time":[],
        "Step Size":[],
        "MPS found":[],
        "Time to complete":[],
        "Number of probes received":[],
        "Notes":[],
        "Start Time":[],
        "IPv":[]
        }
table1 = {"Configured link size":[],
        "Estimated round trip time":[],
        "Configured round trip time":[],
        "Table values":[],
        "MPS found":[],
        "Time to complete":[],
        "Number of probes received":[],
        "Notes":[],
        "Start Time":[],
        "IPv":[]
        }
table2 = {"Configured link size":[],
        "Estimated round trip time":[],
        "Configured round trip time":[],
        "Table values":[],
        "MPS found":[],
        "Time to complete":[],
        "Number of probes received":[],
        "Notes":[],
        "Start Time":[],
        "IPv":[]
        }
for i in data: 
    r = i["res"]
    real_link = i["real_mtu"]
    real_rtt = i["real_rtt"]
    est_rtt = "{0:.4f}".format(i["probe_timer"])
    ii = "ipv"+str(i["ipv"])
    if "step1" in r:
        step1["Configured link size"].append(real_link)  
        step1["IPv"].append(ii)  
        step1["Configured round trip time"].append(real_rtt)  
        step1["Estimated round trip time"].append("{0:.4f}".format(1000*r["step1"]["est_rtt"]))
        step1["Step Size"].append(1)  
        step1["MPS found"].append(r["step1"]["plpmtu"])  
        step1["Time to complete"].append("{0:.4f}".format(r["step1"]["time_taken"]))
        step1["Number of probes received"].append(r["step1"]["count"])
        step1["Notes"].append(r["step1"]["notes"])
        step1["Start Time"].append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(i["time"])))
    if "step7" in r:
        step7["Configured link size"].append(real_link)  
        step7["IPv"].append(ii)  
        step7["Configured round trip time"].append(real_rtt)  
        step7["Estimated round trip time"].append("{0:.4f}".format(1000*r["step7"]["est_rtt"]))
        step7["Step Size"].append(7)  
        step7["MPS found"].append(r["step7"]["plpmtu"])  
        step7["Time to complete"].append("{0:.4f}".format(r["step7"]["time_taken"]))
        step7["Number of probes received"].append(r["step7"]["count"])
        step7["Notes"].append(r["step7"]["notes"])
        step7["Start Time"].append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(i["time"])))
    if "step9" in r:
        step9["Configured link size"].append(real_link)  
        step9["IPv"].append(ii)  
        step9["Configured round trip time"].append(real_rtt)  
        step9["Estimated round trip time"].append("{0:.4f}".format(1000*r["step9"]["est_rtt"]))
        step9["Step Size"].append(9)  
        step9["MPS found"].append(r["step9"]["plpmtu"])  
        step9["Time to complete"].append("{0:.4f}".format(r["step9"]["time_taken"]))
        step9["Number of probes received"].append(r["step9"]["count"])
        step9["Notes"].append(r["step9"]["notes"])
        step9["Start Time"].append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(i["time"])))
    if "table1" in r:
        table1["Configured link size"].append(real_link)  
        table1["IPv"].append(ii)  
        table1["Configured round trip time"].append(real_rtt)  
        table1["Estimated round trip time"].append("{0:.4f}".format(1000*r["table1"]["est_rtt"]))
        table1["Table values"].append("1300 1350")  
        table1["MPS found"].append(r["table1"]["plpmtu"])  
        table1["Time to complete"].append("{0:.4f}".format(r["table1"]["time_taken"]))
        table1["Number of probes received"].append(r["table1"]["count"])
        table1["Notes"].append(r["table1"]["notes"])
        table1["Start Time"].append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(i["time"])))
    if "table2" in r:
        table2["Configured link size"].append(real_link)  
        table2["IPv"].append(ii)  
        table2["Configured round trip time"].append(real_rtt)  
        table2["Estimated round trip time"].append("{0:.4f}".format(1000*r["table2"]["est_rtt"]))
        table2["Table values"].append("1250 1260 1270 1280")
        table2["MPS found"].append(r["table2"]["plpmtu"])  
        table2["Time to complete"].append("{0:.4f}".format(r["table2"]["time_taken"]))
        table2["Time to complete"].append("{0:.4f}".format(r["table2"]["time_taken"]))
        table2["Number of probes received"].append(r["table2"]["count"])
        table2["Notes"].append(r["table2"]["notes"])
        table2["Start Time"].append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(i["time"])))

if step1["MPS found"]:
    with open("step1.csv", "wb") as f:
        writer = csv.writer(f)
        writer.writerow(step1.keys())
        writer.writerows(zip(*step1.values()))
if step7["MPS found"]:
    with open("step7.csv", "wb") as f:
       writer = csv.writer(f)
       writer.writerow(step7.keys())
       writer.writerows(zip(*step7.values()))
if step9["MPS found"]:
    with open("step9.csv", "wb") as f:
       writer = csv.writer(f)
       writer.writerow(step9.keys())
       writer.writerows(zip(*step9.values()))
if table1["MPS found"]:
    with open("table1.csv", "wb") as f:
       writer = csv.writer(f)
       writer.writerow(table1.keys())
       writer.writerows(zip(*table1.values()))
if table2["MPS found"]:
    with open("table2.csv", "wb") as f:
       writer = csv.writer(f)
       writer.writerow(table2.keys())
       writer.writerows(zip(*table2.values()))
