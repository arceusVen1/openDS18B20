#!/usr/bin/python3
from open_ds18b20.fichier import ProbeConfigFile
import re
import os

SETTINGS = {"idt": "", "slug": "", "alert": {"bool": False, "max": 0,
                                             "min": 0}, "thermostated": {"bool": False, "temps": []}, "moment": []}


class Materials:

    """Represents all the probes"""

    def __init__(self):
        self.listprobes = []
        self.listPaths = []
        self.numWorkingProbes = 0
        self.path = os.path.abspath("/sys/bus/w1/devices")
        return

    def detect_probes(self):
        """
        Detects the connected DS18B20 probes whose folders always start by 28

        :return: list of files containing a measured temperature from a probe
        :rtype: list
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


class Probe:

    """Represents the DS18B20 probes"""

    def __init__(self, idt, settings=SETTINGS):
        self.idt = str(idt)
        self.settings = settings
        self.settings["slug"] = self.idt
        self.temperature = ""
        path = "/home/pi/ds18b20_conf/" + self.idt + ".json"
        self.config = ProbeConfigFile(path)
        return

    def is_working(self, line):
        """
        Checks if a probe is working by matching with "YES"
        inside the /sys/bus/w1/.../w1_slave file

        :param line: the fist line of the file which contains "YES"/"NO"
        :type line: str

        :return: the working state of a probe
        :rtype: bool
        """
        regexp = re.compile("YES$")
        if regexp.search(line):
            return True
        else:
            return False

    def has_config(self):
        """
        Tests if the config file exist and has been filled

        :return: indicates if the config file exist with attributes
        :rtype: bool

        """
        if not self.config.exists() or (hasattr(self.config, "nbline") and
                                        self.config.nbline == 0):
            return False
        else:
            self.allow_config()
            return True

    def allow_config(self):
        """creates the config file if needed and then opens it
        """
        self.config.create()
        self.config.edit()

    def get_data(self):
        """
        Reads the data from the config file and
        upload it in the settings

        :return: the loaded settings of the probes with its config
        :rtype: dict

        """
        self.config.get_data()
        self.settings = self.config.settings
        return self.settings

    def set_data(self):
        """
        Overwrites the file with the settings

        :raises ValueError: if the settings remained in their default definition
        """
        if self.settings == SETTINGS:
            raise ValueError("the settings needs to be modified")
        self.config.settings = self.settings
        self.config.register()

    def set_idt(self):
        """set the id of the probe
        """
        self.settings["idt"] = self.idt

    def has_alert(self):
        """
        Test if the config has alert settings

        :return: if the user wants the probe to send alert
        :rtype: bool
        """
        return self.settings["alert"]["bool"]

    def set_alert(self, alert):
        """
        Set the alert bool

        :param alert: True f you want to power alert system on, false otherwise
        :type alert: bool

        :raises TypeError: if alert is not a booleant
        """
        if not isinstance(alert, bool):
            raise TypeError("alert setting is either True or False")
        self.settings["alert"]["bool"] = True

    def get_max_alert(self):
        """
        Get the maximum value suported before alert

        :return: the max temperature allowed before alert
        :rtype: float
        """
        return self.settings["alert"]["max"]

    def get_min_alert(self):
        """
        Get the minimum temp supported before alert

        :return: the min temperature allowed before alert
        :rtype: float
        """

        return self.settings["alert"]["min"]

    def set_max_alert(self, max_alert):
        """
        Set the maximum temperature before alert

        :param max_alert: the maximum temperature desired before alert
        :type max_alert: float

        :raises TypeError: if the max_alert given is not a float
        """
        if not isinstance(max_alert, float):
            raise TypeError("the temperature is a number")
        self.settings["alert"]["max"] = max_alert

    def set_min_alert(self, min_alert):
        """
        Set the minimum temperature before alert

        :param min_alert: the minimum temp
        :type min_alert: float

        :raises TypeError: if the value given is not a float
        """
        if not isinstance(min_alert, float):
            raise TypeError("the temperature is a number")
        self.settings["alert"]["min"] = min_alert

    def get_slug(self):
        """
        Get the pseudo name of the probe

        :return: the pseudo name of the probe
        :rtype: str
        """
        return self.settings["slug"]

    def set_slug(self, slug):
        """
        Sets the pseudo name of the probe

        :param slug: a pseudo name for the probe
        :type slug: str
        """
        self.settings["slug"] = str(slug)

    def is_thermostated(self):
        """
        Tests if the probe has a thermostating option

        :return: True if it is thermostated
        :rtype: bool
        """
        return self.settings["thermostated"]["bool"]

    def set_thermostated(self, bool_, temps=None):
        """
        Sets the thermostats option with the list of thermostats

        :param bool_: True for thermostat option
        :type bool_: bool
        :param temps: (optional) the list of different temps desired if True
        :type temps: (optional) list

        :raises TypeError: if bool_ is not a bool or temp not a list of float
        :raises ValueError: if you choose thermostat option, you need a list of temp
        """
        if temps is None:
            temps = []
        if not isinstance(bool_, bool):
            raise TypeError("thermostated should be a boolean")
        if bool_:
            if not temps:
                raise ValueError("the list of temps desired is empty")
            for i in range(len(temps)):
                if not isinstance(temps[i], float):
                    raise TypeError("the temps must be a list of float")
            self.settings["thermostated"]["temps"] = temps
        self.settings["thermostated"] = bool_

    def get_moment(self):
        """
        Gets the list of time slot for the temps

        :return: the list of the beginning of time slot
        :rtype: list
        """
        return self.settings["moment"]

    def set_moment(self, moments):
        """
        Sets the different time slots by the beginning of each time slot

        :param moments: time slot with the hour written in this form "%H:%M"
        :type list:

        :raises TypeError: if the number of time slots is different from the number of temperatures
        :raises IndexError: if the time slots are not a list
        """
        if not isinstance(moments, list):
            raise TypeError("the moments must be a list")
        if len(moments) != len(self.settings["thermostated"]["temps"]):
            raise IndexError("number of moments must equal temperatures")
        self.settings["moment"] = moments

    def get_creneau(self):
        """
        Returns the number of time slots

        :return: number of time changing fror a thermostat
        :rtype: int
        """
        return len(self.settings["moment"])

    def link_moment_temp(self):
        """
        Associates a temp with a moment

        :return: {time_slot_temp: beginning_of_time_slot}
        :rtype: dict
        """
        thermorange = {}
        for i in range(self.get_creneau()):
            thermorange[self.settings["moment"][i]] = self.settings[
                "thermostated"]["temps"][i]
        return thermorange

    def get_temperature(self, line):
        """
        Gets the temperature measured by the probe
        from the line of its system file

        :param line: the line which contains the temperature
        :type line: str

        :return: the temperature measured
        :rtype: float

        :Example:
            the line looks like this
        """
        regexp = re.compile("\d+$")
        temp = regexp.search(line).group(0)
        temp = list(temp)
        self.temperature = temp[0] + temp[1] + "." + temp[2]
        return self.temperature
