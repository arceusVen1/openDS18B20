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

    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.settings = {}
        return

    def __is_working(self):
        pass


    def get_data(self):
        pass

    def set_data(self):
        pass

    def has_alert(self):
        pass

    def get_slug(self):
        pass

    def __set_slug(self):
        pass

    def get_max(self):
        pass

    def get_min(self):
        pass

    def __set_max(self):
        pass

    def __set_min(self):
        pass

    def get_moment(self):
        pass

    def __set_moment(self):
        pass

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
