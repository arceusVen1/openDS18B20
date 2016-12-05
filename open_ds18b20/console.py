

class Console(object):
	"""display all the needed info in the console"""

	def __init__(self, config):
		super(Screen, self).__init__()
		self.config = config

	def initialConfig(self):
    	"""try to open the config file or creates one if there's not

    	Returns:
        	ConfigFile: the opened config.json file
        """
    	path = "/home/pi/ds18b20_conf"
    	try:
        	os.path.abspath(path)
        	config = fichier.ConfigFile(path + "/config.json")
    	except IOError:
        	print("creating config.json in " + path)
        	try:
            	os.makedirs(path)
        	except OSError:
            	print("already existing folder")
        	subprocess.Popen(["touch", path + "/config.json"])
        	# leaves enough time for the subprocess to create the file
        	time.sleep(1)
        	config = fichier.ConfigFile(path + "/config.json")
    	return config

    def writeDependencies():
    	"""indicates what to do if you don't have the modules installed


    	Returns:
        	bool: just to know that you miss the modules
    	"""
    	print("before continuing you should add "
         	 "\"w1-gpio\" and \"w1-therm\" to /etc/modules files")
    	return False

    	def promptConfig(self, config):
    	"""ask for the new config settings

    	Args:
        	config (ConfigFile): File to write the config

    	Returns:
        	none: The configuration has been saved
    	"""
    	print("adress where emails are going to be send and sent from ? ")
    	SETTINGS["email"] = input(PROMPT)
    	print("password ? "
          	"(warning the password will be kept clear in the config file)")
    	# to hide the password in the console
    	SETTINGS["password"] = getpass.getpass()
    	print("What is the number of probes attached ?")
    	try:
        	SETTINGS["number"] = int(input(PROMPT))
    	except:
        	print("a number please !")
    	print("woud you like to set an alert system ?(y/n)")
    	alert = input(PROMPT)
    	if str(alert) == "y":
        	SETTINGS["alert"]["choice"] = True
        	print("max temp ?")
        	SETTINGS["alert"]["max"] = int(input(PROMPT))
        	print("min temp ?")
        	SETTINGS["alert"]["min"] = int(input(PROMPT))
    	config.register(SETTINGS)
    	return


		
