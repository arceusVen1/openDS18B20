#!/usr/bin/python3

from open_ds18b20.console import Console
import json
import os
import time
import subprocess
import re

SETTINGS = {"email": "", "password": "", "number": 0,
            "alert": {"choice": False, "max": 0, "min": 0}}


class File(object):

    """abstract class of file"""

    def __init__(self, filepath):
        self.path = filepath
        self.file = open(self.path, "r")
        self.content = list(self.file)
        self.nbline = len(self.content)

    def readLine(self, nbline):
        """Reads a specific line

        Args:
            nbline (int): number of the line

        Returns:
            str: the content read
        """
        return self.content[nbline - 1]

    def closeFile(self):
        """close a file

        Returns:
            none: File has been closed
        """
        self.file.close()

    def removeFile(self):
        self.closeFile()
        os.remove(self.path)


class ConfigFile(File):

    """Deal with the configuration file in /home/pi/ds18b20_conf/config.json"""

    def __init__(self, filepath):
        self.path = filepath
        self.settings = SETTINGS
        console = Console()
        osPath = os.path.abspath(self.path)
        if not os.path.exists(osPath):
            dirpath = os.path.dirname(osPath)
            console.display("creating config.json in " + str(dirpath))
            try:
                os.makedirs(dirpath)
            except OSError:
                console.display("already existing folder")
            subprocess.Popen(["touch", self.path])
            # leaves enough time for the subprocess to create the file
            time.sleep(1)
        self.file = open(self.path, 'r')
        self.content = list(self.file)
        self.nbline = len(self.content)

    def readData(self):
        """load the data from a json file

        Returns:
            none: The datas have been loaded
        """
        self.file.seek(0)
        self.data = json.load(self.file)

    def getCredentials(self):
        """get the credential from the json loaded data

        Returns:
            str: email and password from the data
        """
        email = self.data["email"]
        password = self.data["password"]
        return email, password

    def has_alert(self):
        """determine if the configuration includes alert mailing

        Returns:
            bool: True if it has alert, False otherwise
        """
        if self.data["alert"]["choice"]:
            return True
        else:
            return False

    def getProbes(self):
        return int(self.data["number"])

    def getMaxTempAlert(self):
        """get the max temperature allowed before alert from the json loaded data

        Returns:
            float: maximum temperature allowed
        """
        return float(self.data["alert"]["max"])

    def getMinTempAlert(self):
        """Get the minimum temperature allowed before alert from the json loaded data

        Returns:
            float: Minimum temp allowed
        """
        return float(self.data["alert"]["min"])

    def set_settings(self):
        self.settings = Console().promptConfig(self.settings)
        self.register()

    def register(self):
        """Registers the (new) settings in the cofnig file

        Returns:
            none: The settings hacve been saved in the config file
        """
        element = json.dumps(self.settings, indent=4)
        self.__save(element)

    def __save(self, element):
        """Overwrite text in a file to ensure that the file have been saved

        Args:
            element (str): what needs to be written

        Returns:
            none: The file has been correctly overwrittent by the element
        """
        self.file = open(self.path, "w")
        self.file.write(element)
        self.file.close()
        self.file = open(self.path, "r")

    def closeFile(self):
        super(ConfigFile, self).closeFile()


class ProbeConfigFile(ConfigFile):
    """deals with the config file of the probes"""

    def __init__(self, path):
        # super(ProbeConfigFile, self).__init__()
        self.path = path

    def register(self):
        super(ProbeConfigFile, self).register()

    def __save(self):
        super(ProbeConfigFile, self).__save()

    def readData(self):
        super(ProbeConfigFile, self).readData()


class ProbeFile(File):

    """Deals with the file generated by the connected probes"""

    def __init__(self, filepath):
        super(ProbeFile, self).__init__(filepath)

    def closeFile(self):
        super(ProbeFile, self).closeFile()


class ModuleFile(File):

    """Deals with the file /etc/modules"""

    def __init__(self, filepath):
        super(ModuleFile, self).__init__(filepath)

    def closeFile(self):
        super(ModuleFile, self).closeFile()

    def tester(self):
        """test the presence w1-therm and w1-gpio modules in the /etc/modules

        Returns:
            bool: True if the modules are installed, false otherwise
        """
        flag = [False, False]
        for i in range(self.nbline):
            line = self.readLine(i + 1)
            if re.match(r"^w1-gpio", line):
                flag[0] = True
            if re.match(r"^w1-therm", line):
                flag[1] = True
        if flag != [True, True]:
            return Console.writeDependencies()
        else:
            return True
