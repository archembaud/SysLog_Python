# Simple System Monitoring using PSUtil for Keck Program
# Should be easily plugged in to Kraken controller.
# Matt Smith and Lewis Lakerink

import psutil as ps
import sys, time
import numpy as np
import os
import subprocess
from datetime import datetime


def CallNvidiaSMI():
	# Call the Nvidia SMI to get the temperature
        a = 'nvidia-smi -q -d temperature | grep \'GPU Current Temp\''
	#print a
	b = os.popen(a, 'r', 1)
	result = b.read()
	print result
	

def bytes2human(n):
	# Convert from bytes to something readable
	symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
	prefix = {}
	for i, s in enumerate(symbols):
		prefix[s] = 1 << (i + 1) * 10
	for s in reversed(symbols):
		if n >= prefix[s]:
			value = float(n) / prefix[s]
			return '%.2f %s' % (value, s)
	return '%.2f B' % (n)


def GetCPUUsage(verbose):
	# Return an array holding CPU usage
	CPU_data = ps.cpu_percent(interval=1.0, percpu=True)
	cores = ps.cpu_count()
	busy_core_count = 0;
	for i in range(cores):
		if (CPU_data[i]>10):
			busy_core_count = busy_core_count + 1

	if (verbose==True):
		print CPU_data
		print("Found %d cores busy" % busy_core_count)

	return CPU_data, busy_core_count

def GetNetUsage(interval):
	# Return the net statistics
	tot_before = ps.net_io_counters()
	pnic_before = ps.net_io_counters(pernic=True)
	# sleep some time
	time.sleep(interval)
	tot_after = ps.net_io_counters()
	pnic_after = ps.net_io_counters(pernic=True)
	return (tot_before, tot_after, pnic_before, pnic_after)


def ReportNetUsage(tot_before, tot_after, pnic_before, pnic_after):
	# Print the Network Stats
	#print("Total Bytes sent and recieved: %s, %s" % (bytes2human(tot_after.bytes_sent),bytes2human(tot_after.bytes_recv)))
	nic_names = list(pnic_after.keys())
	nic_names.sort(key=lambda x: sum(pnic_after[x]), reverse=True)
	for name in nic_names:
        	stats_before = pnic_before[name]
        	stats_after = pnic_after[name]
		diff = stats_after.bytes_sent - stats_before.bytes_sent
		if (diff > 0):
			print("Bytes sent on %s = %s" % (name, diff))
		diff = stats_after.bytes_recv - stats_before.bytes_recv
		if (diff > 0):
			print("Bytes recv on %s = %s" % (name, diff))



def GetTemperatures(verbose):	
    	# Get the number of cores
	cores = ps.cpu_count()
	T_raw_data = np.zeros(2*cores)
	T_data_elements = 0; 
	if not hasattr(ps, "sensors_temperatures"):
		print("System Temperature monitorage not supported")
	else:
		# Get sensor info
		temps = ps.sensors_temperatures()
		if not temps:
			sys.exit("Cant read any temperatures")
		else:
			for name, entries in temps.items():
				for entry in entries:
					T_raw_data[T_data_elements] = entry.current
					T_data_elements = T_data_elements + 1
					if (verbose==True):
						print("	%-20s %s C (high = %s C, max = %s C)" % (entry.label or name, entry.current, entry.high, entry.critical))
						print()

	return T_raw_data, T_data_elements



# Main Script

# Test out something
# print bytes2human(100001221)

# Test some scripts
print("======== Monitoring System ==========")

# Stuff for parsing nvidia-smi
cmd = 'nvidia-smi -q -d temperature | grep \'GPU Current Temp\''

# Open a file for writing the log
F = open("systemlog.txt","w")
F.write("Time \t \t Max Temp\n")
try:
	while True:
		        CPU_Usage, Busy_Cores = GetCPUUsage(False)
			CPU_Usage.sort()
			No_Cores = len(CPU_Usage)
			# Report without new line (Python 2.X, v3 uses another way)
			F.write(str(datetime.now().time())),
			print("CPU Usage: %d Busy Cores - Loading = " % Busy_Cores),
			for i in range(Busy_Cores):
				print("%d" % (CPU_Usage[No_Cores-i-1])),
				print("  (Percent)")
			Temp, No_Temp = GetTemperatures(False)
			F.write("\t \t"),
			F.write(str(np.amax(Temp)))
			F.write("\n")
			print("Maximum temperature in server = %d degrees C" % (np.amax(Temp)))
			CallNvidiaSMI()
			Pipe = os.popen(cmd, 'r', 1)
			result = Pipe.read()
			F.write(result)


except KeyboardInterrupt:
    pass

# Close the file
F.close()

print("Ceased the measurement loop")
