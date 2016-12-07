#!/usr/bin/python3
from fichier import ProbeConfigFile
import re
import os

SETTINGS = {"idt": "", "alert": {"bool": False, "max": 0,
                                 "min": 0}, "max": [], "min": [], "moment": []}


class Materials():

    """Represents all the probes"""

    def __init__(self):
        self.listprobes = []
        self.listPaths = []
        self.numWorkingProbes = 0
        self.path = os.path.abspath("/sys/bus/w1/devices")
        return

    def detectProbes(self):
        """detects the connected DS18B20 probes whose folders always start by 28

        Returns:
            list: files containing a measured temperature from a probe
        """
        regexp = re.compile("^28")
        for directory in os.listdir(self.path):
            if regexp.search(directory):
                self.listprobes.append(directory)
        self.__path_listing()
        return self.listprobes

    def __path_listing(self):
        for probe in range(len(self.listprobes)):
            self.listPaths.append(
                self.path + '/' + self.listprobes[probe] + "/w1_slave")


class Probe():

    """Represents the DS18B20 probes"""

    def __init__(self, idt, settings=SETTINGS):
        self.idt = idt
        self.settings = settings
        self.temperature = ""
        self.path = "/home/pi/ds18b20_conf/" + self.idt + ".json"
        self.config = ProbeConfigFile(self.path)
        return

    def is_working(self, line):
        regexp = re.compile("YES$")
        if regexp.search(line):
            return True
        else:
            return False

    def __has_config(self):
        if not self.config.exists():
            self.config.create()
            return False
        elif hasattr(self.config, "nbline") and self.config.nbline == 0:
            return False
        else:
            return True

    def get_data(self):
        if self.__has_config():
            self.config.edit()
            self.settings = self.config.readData()
        return self.settings

    def set_data(self):
        self.config.settings = self.settings
        self.config.register()

    def set_idt(self):
        self.settings["idt"] = self.idt

    def has_alert(self):
        if self.settings["alert"]["bool"]:
            return True
        else:
            return False

    def set_max_alert(self, maxAlert):
        self.settings["alert"]["max"] = maxAlert

    def set_min_alert(self, minAlert):
        self.settings["alert"]["min"] = minAlert

    def get_slug(self):
        return self.settings["slug"]

    def set_slug(self, slug):
        self.settings["slug"] = str(slug)

    def get_max(self):
        return self.settings["max"]

    def get_min(self):
        return self.settings["min"]

    def set_max(self, maxTemps):
        self.settings["max"] = maxTemps

    def set_min(self, minTemps):
        self.settings["min"] = minTemps

    def get_moment(self):
        return self.settings["moment"]

    def set_moment(self, moments):
        self.settings["moment"] = moments

    def get_creneau(self):
        return len(self.settings["moment"])

    def link_moment_temp(self):
        thermoRange = []
        for i in range(self.get_creneau()):
            thermoRange.append([self.settings["moment"][i],
                                self.settings["min"][i],
                                self.settings["max"][i]])
        return thermoRange

    def getTemperature(self, line):
        """get the temperature

        Args:
            line (str): content of the files with the temperature inside

        Returns:
            string: String of the temperatures
        """
        regexp = re.compile("\d+$")
        temp = regexp.search(line).group(0)
        temp = list(temp)
        self.temperature = temp[0] + temp[1] + "." + temp[2]
        return self.temperature
