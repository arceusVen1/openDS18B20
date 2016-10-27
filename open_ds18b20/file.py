import json
import re

#from abc import ABCMeta, abstractmethod

class File(object):


	def __init__(self, filepath):
		self.path = filepath
		self.file = open(self.path,"r")
		self.content = list(self.file)
		self.nbline = len(self.content)

	def closeFile(self):
		self.file.close()


class ConfigFile(File):
	
	def __init__(self, filepath):
	 	super(ConfigFile, self).__init__(filepath)

	def readData(self):
		self.file.seek(0)
		self.data = json.load(self.file)

	def getCredentials(self):
	 	email = self.data["email"]
	 	password = self.data["password"]
	 	return email, password

	def has_alert(self):
		if self.data["alert"]["choice"] == True:
			return True
		else:
			return False

	def getMaxTempAlert(self):
		return float(self.data["alert"]["max"])

	def getMinTempAlert(self):
		return float(self.data["alert"]["min"])

	def register(self, settings):
		element = json.dumps(settings, indent=4)
		self._save(element)
		
	def _save(self, element):
		self.file = open(self.path, "w")
		self.file.write(element)
		self.file.close()
		self.file = open(self.path, "r")
	
	def closeFile(self):
	 	super(ConfigFile, self).closeFile()



class ProbeFile(File):

	def __init__(self, filepath):
		super(ProbeFile, self).__init__(filepath)

	def readLine(self, nbline):
		return self.content[nbline-1]

	def closeFile(self):
		super(ProbeFile, self).closeFile()

class ModuleFile(File):
	def __init__(self, filepath):
		super(ModuleFile, self).__init__(filepath)

	def readLine(self, nbline):
		return self.content[nbline-1]
	
	
	def closeFile(self):
		super(ModuleFile, self).closeFile()
	
