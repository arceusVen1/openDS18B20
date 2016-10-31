#!/usr/bin/python3
import sys
import os
import re
import getpass
import time
import subprocess
import file, mail, probe

#--GLOBAL---------------------------------------------------------------------

SETTINGS = {"email":"","password":"","alert":{"choice": False, "max":0, "min":0}}
PROMPT = '> '

#-----------------------------------------------------------------------------


def to_float(array):
	"""turn a list's integer in float
	
	Args:
	    array (ARRAY): array of number
	
	Returns:
	    ARRAY: the same array with float numbers
	"""
	floater = []
	for i in range(len(array)):
		floater.append(float(array[i]))
	return floater

def initialConfig():
	"""try to open the config file or creates one if there's not
	
	Returns:
	    JSON: the opened config.json file
	"""
	path = "/home/pi/ds18b20_conf"
	try: 
		os.path.abspath(path)
		config = file.ConfigFile(path + "/config.json")
	except IOError:
		print("creating config.json in " + path)
		try:
			os.makedirs(path)
		except OSError:
			print("already existing folder")
		subprocess.Popen(["touch", path + "/config.json"])
		time.sleep(1) #leaves enough time for the subprocess to create the file
		config = file.ConfigFile(path + "/config.json")
	return config
	

def writeDependencies():
	"""indicates what to do if you don't have the modules installed
	
	
	Returns:
	    BOOLEAN: just to know that you miss the modules
	"""
	print("before continuing you should add \"w1-gpio\" and \"w1-therm\" to /etc/modules files")
	return False

def promptConfig(config):
	"""ask for the new config settings
	
	Args:	
	    config (JSON): File to write the config
	
	Returns:
	    none: The configuration has been saved
	"""
	print("adress where emails are going to be send and sent from ? ")
	SETTINGS["email"] = raw_input(PROMPT)
	print("password ? (warning the password will be kept clear in the config file)")
	SETTINGS["password"]= getpass.getpass() #to hide the password in the console
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
	"""test the presence w1-therm and w1-gpio modules in the /etc/modules
	
	Returns:
	    TYPE: True if the modules are installed, false otherwise
	"""
	flag = [False, False]
	modules = file.ModuleFile("/etc/modules")
	for i in range(modules.nbline):
		line = modules.readLine(i+1)
		if re.match(r"^w1-gpio", line):
			flag[0] = True
		if re.match(r"^w1-therm", line):
			flag[1] = True
	if flag != [True, True]:
		return writeDependencies()
	else:
		return True

def createMail(probes, subject, config, alert=False):
	"""create the email in a more compact fashion to use it miore easily on the __main__
	
	Args:
	    probes (PROBE): Probe instance
	    subject (STRING): Subject of the message
	    config (CONFIG): Config file
	    alert (bool, optional): if it is an alert mail
	
	Returns:
	    none: mail has been sent
	"""
	email = mail.Mail()
	email.messageBody(probes.temperatures, alert)
	email.credentials["email"], email.credentials["password"] = config.getCredentials()
	email.messageBuilder(email.credentials["email"], email.credentials["email"], subject)
	email.sendMail()
	
def main():
	tester = modulesTester() 	#test that the moduels are present
	if tester == False:			#
		return 					#
	files = []
	if len(sys.argv) > 1:		#if the erase arg has been given the config is reset
		if str(sys.argv[1]) == "erase":
			os.remove("/home/pi/ds18b20_conf/config.json") 	#erase the config file to avoid conflict
	config = initialConfig()	#create if needed and open a config file
	if config.nbline ==  0:		#if the config file is empty (especially if it has just been created)
		promptConfig(config)	#ask for the new settings in the console
	config.readData()			#read the data now that you should have some
	probes = probe.Probe()		#create a Probe instance
	probes.detectProbe()		#detect the probes attach
#	dht_h, dht_t = dht.read_retry(dht.DHT22,17)
	try:						#try to read the probes temp 
		for p in range(len(probes.listprobes)):
			files.append(file.ProbeFile(probes.listprobes[p]))
			templine = files[p].readLine(2)
			probes.getTemperature(templine)
	except: 					# return an exception with the nature of the exception
		message = "temperatures couldn't be read : ", sys.exc_info()[:2] 
		return message
	try:	
		mailsent = False 		#a flag to avoid sending a standard mail + alert
		floater = to_float(probes.temperatures) 	#transform the temp in float
		if config.has_alert():	#if alert has been enable compare the max and min conf ith the actual temp
			if max(floater) >= config.getMaxTempAlert() or min(floater) <= config.getMinTempAlert():
				subject = "Alert detected"
				createMail(probes, subject, config, True)
				mailsent = True		#a mail has been sent
		if len(sys.argv) >= 2 and mailsent == False: #to force a mail message with the optionnal argument "mail"
			if str(sys.argv[1]) == "mail":
				subject = "list of temperatures"
				createMail(probes, subject, config)
		
	except:
		return "mail couldn't be send : ", sys.exc_info()
	for i in range(len(files)):		#close the open filed
		files[i].closeFile()
	config.closeFile()	
	return (probes.temperatures)

if __name__ == '__main__':
	sys.exit(main())



	

