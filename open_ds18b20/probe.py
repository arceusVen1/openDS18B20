#!/usr/bin/python3
from open_ds18b20.fichier import ProbeConfigFile
import re
import os

SETTINGS = {"idt": "", "slug": "", "alert": {"bool": False, "max": 0,
                                             "min": 0}, "thermostated": {"bool": False, "temps": []}, "moment": []}


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
        self.settings["slug"] = self.idt
        self.temperature = ""
        path = "/home/pi/ds18b20_conf/" + self.idt + ".json"
        self.config = ProbeConfigFile(path)
        return

    def is_working(self, line):
        regexp = re.compile("YES$")
        if regexp.search(line):
            return True
        else:
            return False

    def has_config(self):
        """test if the config file exist and has been filled

        Returns:
            bool: true if the config exists, false otherwise
        """
        if not self.config.exists() or (hasattr(self.config, "nbline") and
                                        self.config.nbline == 0):
            return False
        else:
            self.allow_config()
            return True

    def allow_config(self):
        self.config.create()
        self.config.edit()

    def get_data(self):
        self.config.readData()
        self.settings = self.config.settings
        return self.settings

    def set_data(self):
        self.config.settings = self.settings
        self.config.register()

    def set_idt(self):
        self.settings["idt"] = self.idt

    def has_alert(self):
        return self.settings["alert"]["bool"]

    def set_alert(self, alert):
        self.settings["alert"]["bool"] = True

    def get_max_alert(self):
        return self.settings["alert"]["max"]

    def get_min_alert(self):
        return self.settings["alert"]["min"]

    def set_max_alert(self, maxAlert):
        self.settings["alert"]["max"] = float(maxAlert)

    def set_min_alert(self, minAlert):
        self.settings["alert"]["min"] = float(minAlert)

    def get_slug(self):
        return self.settings["slug"]

    def set_slug(self, slug):
        slug = str(slug)
        self.settings["slug"] = str(slug)

    def is_thermostated(self):
        return self.settings["thermostated"]["bool"]

    def set_thermostated(self, bool_, temps=[]):
        if not isinstance(bool_, bool):
            raise TypeError("thermostated should be a boolean")
        if bool_:
            if temps == []:
                raise ValueError("the list of temps desired is empty")
            for i in range(len(temps)):
                if not isinstance(temps[i], float):
                    raise TypeError("the temps must be a list of float")
            self.settings["thermostated"]["temps"] = temps
        self.settings["thermostated"] = bool_

    def get_moment(self):
        return self.settings["moment"]

    def set_moment(self, moments):
        if not isinstance(moments, list):
            raise TypeError("the moments must be a list")
        if len(moments) != len(self.settings["thermostated"]["temps"]):
            raise IndexError("number of moments must equal temperatures")
        self.settings["moment"] = moments

    def get_creneau(self):
        return len(self.settings["moment"])

    def link_moment_temp(self):
        thermorange = {}
        for i in range(self.get_creneau()):
            thermorange[self.settings["moment"][i]] = self.settings[
                "thermostated"]["temps"][i]
        return thermorange

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
