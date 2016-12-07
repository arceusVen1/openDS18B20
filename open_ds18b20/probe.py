#!/usr/bin/python3
from fichier import ProbeConfigFile
import re
import os


class Probes():

    """Represents all the probes"""

    def __init__(self):
        self.listprobes = []
        self.temperatures = []
        self.path = os.path.abspath("/sys/bus/w1/devices")
        return

    def detectProbes(self):
        """detects the connected DS18B20 probes whose folders always start by 28

        Returns:
            list: files containing a measured temperature from a probe
        """
        regexp = re.compile("^28")
        for directory in os.listdir(self.path):
            if regexp.match(directory):
                self.listprobes.append(
                    self.path + '/' + directory + "/w1_slave")
        return self.listprobes

    def __is_working(self):
        pass


class Probe():

    """Represents the DS18B20 probes"""

    def __init__(self, path, settings):
        self.path = os.path.abspath(path)
        self.settings = settings
        return

    def __is_working(self):
        pass

    def get_data(self):
        self.settings = ProbeConfigFile(configPath).readData()
        return self.settings

    def set_data(self):
        self.config.settings = self.settings
        self.config.register()

    def has_alert(self):
        if self.settings["alert"]:
            return True
        else:
            return False

    def __set_max_alert(self, maxAlert):
        self.settings["alert"]["max"] = maxAlert


    def __set_max_alert(self, minAlert):
        self.settings["alert"]["min"] = minAlert

    def get_slug(self):
        return self.settings["slug"]

    def __set_slug(self, slug):
        self.settings["slug"] = str(slug)

    def get_max(self):
        return self.settings["max"]

    def get_min(self):
        return self.settings["min"]

    def __set_max(self, maxTemps):
        self.settings["max"] = maxTemps

    def __set_min(self, minTemps):
        self.settings["min"] = minTemps

    def get_moment(self):
        return self.settings["moment"]

    def __set_moment(self, moments):
        self.settings["moment"] = moments

    def getTemperature(self, line):
        """get the temperature

        Args:
            line (str): content of the files with the temperature inside

        Returns:
            list: List of the temperatures
        """
        regexp = re.compile("\d+$")
        temp = regexp.search(line).group(0)
        temp = list(temp)
        self.temperatures.append(temp[0] + temp[1] + "." + temp[2])
        return self.temperatures
