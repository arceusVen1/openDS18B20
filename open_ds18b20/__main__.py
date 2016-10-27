import sys
import os
import re
import getpass
import time
import subprocess
#import Adafruit_DHT as dht
import file, mail, probe



SETTINGS = {"email":"","password":"","alert":{"choice": False, "max":0, "min":0}}
PROMPT = '> '


def to_float(array):
	floater = []
	for i in range(len(array)):
		floater.append(float(array[i]))
	return floater

def initialConfig():
	path = "/home/pi/ds18b20_conf"
	try: 
		os.path.abspath(path)
		config = file.ConfigFile(path + "/config.json")
	except IOError:
		print "creating config.json in " + path
		try:
			os.makedirs(path)
		except OSError:
			print "already existing folder"
		subprocess.Popen(["touch", path + "/config.json"])
		time.sleep(1) #leaves enough time for the subprocess to create the file
		config = file.ConfigFile(path + "/config.json")
	return config
	

def writeDependencies(file):
	print "before continuing you should add \"w1-gpio\" and \"w1-therm\" to /etc/modules files"
	return False

def promptConfig(config):
	print("adress where emails are going to be send and sent from ? ")
	SETTINGS["email"] = raw_input(PROMPT)
	print("password ? (warning the password will be kept clear in the config file)")
	SETTINGS["password"]= getpass.getpass()
	print("woud you like to set an alert system ?(y/n)")
	alert = raw_input(PROMPT)
	if str(alert) == "y": 
		SETTINGS["alert"]["choice"] = True
		print("max temp ?")
		SETTINGS["alert"]["max"] = int(raw_input(PROMPT))
		print("min temp ?")
		SETTINGS["alert"]["min"] = int(raw_input(PROMPT))
	config.register(SETTINGS)
	return 

def modulesTester():
	flag = [False, False]
	modules = file.ModuleFile("/etc/modules")
	for i in range(modules.nbline):
		line = modules.readLine(i+1)
		if re.match(r"^w1-gpio", line):
			flag[0] = True
		if re.match(r"^w1-therm", line):
			flag[1] = True
	if flag != [True, True]:
		return writeDependencies(modules)

def createMail(probes, subject, config, alert=False):
	email = mail.Mail()
	email.messageBody(probes.temperatures, alert)
	email.credentials["email"], email.credentials["password"] = config.getCredentials()
	email.messageBuilder(email.credentials["email"], email.credentials["email"], subject)
	email.sendMail()
	
def main():
	tester = modulesTester()
	if tester == False:
		return
	files = []
	config = initialConfig()
	if len(sys.argv) > 1:
		if str(sys.argv[1]) == "erase":
			os.remove("/home/pi/ds18b20_conf/config.json")
			config = initialConfig()
			promptConfig(config)
			config.readData()
	elif config.nbline ==  0:
		promptConfig(config)
	config.readData()
	probes = probe.Probe()
	probes.detectProbe()
#	dht_h, dht_t = dht.read_retry(dht.DHT22,17)
	try:		
		for p in range(len(probes.listprobes)):
			files.append(file.ProbeFile(probes.listprobes[p]))
			templine = files[p].readLine(2)
			probes.getTemperature(templine)
	except:
		print "temperatures couldn't be read : ", sys.exc_info()[:2]
	try:	
		mailsent = False
		floater = to_float(probes.temperatures)
		if config.has_alert():
			if max(floater) >= config.getMaxTempAlert() or min(floater) <= config.getMinTempAlert():
				subject = "Alert detected"
				createMail(probes, subject, config, True)
				mailsent = True		
		if len(sys.argv) >= 2 and mailsent == False:
			if str(sys.argv[1]) == "mail":
				subject = "list of temperatures"
				createMail(probes, subject, config)
		
	except:
		print "mail couldn't be send : ", sys.exc_info()
	for i in range(len(files)):
		files[i].closeFile()
	config.closeFile()
	return (probes.temperatures)

if __name__ == '__main__':
	sys.exit(main())



	

