#!/usr/bin/python
import file
import re
import os
import Adafruit_DHT as dht

class Probe():

	def __init__(self):
		self.listprobes = []
		self.temperatures = []
		self.path = os.path.abspath("/sys/bus/w1/devices")
		return


	def getTemperature(self, line):
		regexp = r"\d+$"
		temp = re.search(regexp, line).group(0)
		temp = list(temp)
		self.temperatures.append(temp[0]+temp[1]+"."+temp[2])
		return self.temperatures

	def detectProbe(self):
		regexp = r"^28"
		for directory in os.listdir(self.path):
			if re.match(regexp, directory):
				self.listprobes.append(self.path+'/'+directory + "/w1_slave")
		return self.listprobes
