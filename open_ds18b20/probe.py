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
        self.idt = str(idt)
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
        """creates the config file if needed and then opens it
        """
        self.config.create()
        self.config.edit()

    def get_data(self):
        """read the data from the config file and
        upload it in the settings

        Returns:
            dict: the loaded settings
        """
        self.config.readData()
        self.settings = self.config.settings
        return self.settings

    def set_data(self):
        """registers the new data in the config file

        Raises:
            ValueError: if the settings hasn't been modified
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
        """test if the config has alert settings

        Returns:
            bool: True if alerts are set, False otherwise
        """
        return self.settings["alert"]["bool"]

    def set_alert(self, alert):
        """set the alert bool

        Args:
            alert (bool): alert boolean

        Raises:
            TypeError: if alert is not a booleant
        """
        if not isinstance(alert, bool):
            raise TypeError("alert setting is either True or False")
        self.settings["alert"]["bool"] = True

    def get_max_alert(self):
        """get the maximum value suported before alert

        Returns:
            float: the max temperature allowed
        """
        return self.settings["alert"]["max"]

    def get_min_alert(self):
        """get the minimum temp supported before alert

        Returns:
            float: the min temperature allowed
        """
        return self.settings["alert"]["min"]

    def set_max_alert(self, maxAlert):
        """set the maximum temperature before alert

        Args:
            maxAlert (float): the maximum temp

        Raises:
            TypeError: if the value given is not a float
        """
        if not isinstance(maxAlert, float):
            raise TypeError("the temperature is a number")
        self.settings["alert"]["max"] = maxAlert

    def set_min_alert(self, minAlert):
        """set the minimum temperature before alert

        Args:
            minAlert (float): the minimum temp

        Raises:
            TypeError: if the value given is not a float
        """
        if not isinstance(minAlert, float):
            raise TypeError("the temperature is a number")
        self.settings["alert"]["min"] = minAlert

    def get_slug(self):
        """get the pseudo name of the probe

        Returns:
            str: the speudo name of the probe
        """
        return self.settings["slug"]

    def set_slug(self, slug):
        """set the pseudo name of the probe

        Args:
            slug (str): a pseudo name for the probe
        """
        self.settings["slug"] = str(slug)

    def is_thermostated(self):
        """test if the probe has a thermostating option

        Returns:
            bool: True if it is thermostated
        """
        return self.settings["thermostated"]["bool"]

    def set_thermostated(self, bool_, temps=[]):
        """set the thermostats option with the list of thermostats

        Args:
            bool_ (bool): True for thermostat option
            temps (list, optional): the list of different temps desired if True

        Raises:
            TypeError: if bool_ is not a bool or temp not a list of float
            ValueError: if you choose thermostat option, you need a list of temp 
        """
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
        """get the list of time slot for the temps

        Returns:
            list: list of the beginning of time slot
        """
        return self.settings["moment"]

    def set_moment(self, moments):
        """set the different time slots by the beginning of each time slot

        Args:
            moments (list): time slot with the hour written in this form "%H:%M"

        Raises:
            IndexError: if the number of time slots is different from the number of temps
            TypeError: if the time slots are not a list
        """
        if not isinstance(moments, list):
            raise TypeError("the moments must be a list")
        if len(moments) != len(self.settings["thermostated"]["temps"]):
            raise IndexError("number of moments must equal temperatures")
        self.settings["moment"] = moments

    def get_creneau(self):
        """return the number of time slots

        Returns:
            int: number of time slot
        """
        return len(self.settings["moment"])

    def link_moment_temp(self):
        """associate a temp with a moment

        Returns:
            dict: {time_slog_beginning: temperature}
        """
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
