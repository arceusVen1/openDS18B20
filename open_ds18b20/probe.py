#!/usr/bin/python3
import re
import os


class Probe():

    """Represents the DS18B20 probes"""

    def __init__(self):
        self.listprobes = []
        self.temperatures = []
        self.path = os.path.abspath("/sys/bus/w1/devices")
        return

    def detectProbe(self):
        """detects the connected DS18B20 probes whose folders always start by 28

        Returns:
            LIST: files containing a measured temperature from a probe
        """
        regexp = r"^28"
        for directory in os.listdir(self.path):
            if re.match(regexp, directory):
                self.listprobes.append(self.path + '/' + directory + "/w1_slave")
        return self.listprobes

    def getTemperature(self, line):
        """get the temperature

        Args:
            line (STRING): content of the files with the temperature inside

        Returns:
            LIST: List of the temperatures
        """
        regexp = r"\d+$"
        if re.match(regexp, line):
            temp = re.search(regexp, line).group(0)
            temp = list(temp)
            self.temperatures.append(temp[0] + temp[1] + "." + temp[2])
            return self.temperatures
        else:
            return False
