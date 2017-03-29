#!/usr/bin/python3
"""
TODO:   - {ds18b20: [{}], dht22:[{idt, slug, alert {bool max, min}, hygrostated {bool hygro moment]
        - the id of a dht22 needs to be properly defined (pin)
        - main -> check if len(temperature) may be useless -> test it

"""
import open_ds18b20.fichier as f
import re
import os
import Adafruit_DHT

PATH = "/home/pi/ds18b20_conf/probes/config.json"
SETTINGS = {"idt": "", "slug": "", "alert": {"bool": False, "max": 0,
                                             "min": 0}, "stated": {"bool": False, "values": [], "moment": []}}


class Materials:

    """Represents all the probes"""

    def __init__(self):
        self.listprobes = []
        self.listPaths = {}
        self.num_working_probes = 0
        self.path = os.path.abspath("/sys/bus/w1/devices")
        self.config = f.ProbeConfigFile(PATH)
        self.settings = {"ds18b20": [], "dht22": []}
        return

    def has_config(self):
        """
        Tests if the config file exist and has been filled

        :return: True if the config exists, false otherwise
        :rtype: bool
        """
        if not self.config.exists() or (hasattr(self.config, "nbline") and
                                        self.config.nbline == 0):
            return False
        else:
            self.allow_config()
            return True

    def allow_config(self):
        """
        Creates the file if needed and open it
        """
        self.config.create()
        self.config.edit()

    def get_data(self):
        """
        Loads the data and change the settings to match the data

        :return: the new settings
        :rtype: dict
        """
        self.config.get_data()
        self.settings = self.config.settings
        return self.settings

    def set_data(self):
        """
        Registers the settings in the config and rename the file properly
        """
        self.config.settings = self.settings
        self.config.register()

    def add_probe(self, probe):
        """
        Adds a probe configuration to the main file or modify an existing one

        :param probe: a dht22 or ds18b20 to add or modify
        :type probe: Probe

        :raises TypeError: if the probe is not a probe object
        """
        if not isinstance(probe, Probe):
            raise TypeError("no correct probe given")
        idt = probe.get_id()
        fprobe, i = self.get_probe_by_id(idt)
        if not fprobe:
            if isinstance(probe, Ds18b20):
                self.settings["ds18b20"].append(probe.settings)
            elif isinstance(probe, Dht22):
                self.settings["dht22"].append(probe.settings)
        else:
            if isinstance(probe, Ds18b20):
                self.get_ds18b20()[i] = probe.settings
            elif isinstance(probe, Dht22):
                self.get_dht22()[i - len(self.get_ds18b20())] = probe.settings

    def get_ds18b20(self):
        """
        Gets the configured ds18b20 probes

        :return: the list of the configured ds18b20
        :rtype: list
        """
        return self.settings["ds18b20"]

    # working
    def get_probe_by_id(self, idt, probes=None):
        if not probes:
            probes = self.get_ds18b20() + self.get_dht22()
        for i in range(len(probes)):
            if probes[i]["idt"] == idt:
                return probes[i], i
        return None, None

    def get_probe_by_slug(self, slug, probes=None):
        if not probes:
            probes = self.get_ds18b20() + self.get_dht22()
        for i in range(len(probes)):
            if probes[i]["slug"] == slug:
                return probes[i], i
        return None, None

    #not working
    def get_ds18b20_by_id(self, idt):
        probes = self.get_ds18b20()
        fprobe = self.get_probe_by_id(idt, probes)
        return fprobe

    def get_ds18b20_by_slug(self, slug):
        probes = self.get_ds18b20()
        fprobe = self.get_probe_by_slug(slug, probes)
        return fprobe

    def get_dht22_by_id(self, idt):
        probes = self.get_dht22()
        fprobe = self.get_probe_by_id(idt, probes)
        return fprobe

    def get_dht22_by_slug(self, slug):
        probes = self.get_dht22()
        fprobe = self.get_probe_by_id(slug, probes)
        return fprobe

    def get_dht22(self):
        """
        Gets the configured dht22 probes

        :return: the list of the configured dht22
        :rtype: list
        """
        return self.settings["dht22"]

    def detect_attached_probes(self):
        """
        Detects the connected DS18B20 probes whose folders always start by 28.
        Unfortunately the DHT22 cannot be detected by such means.

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
            self.listPaths[self.listprobes[probe]] = self.path + '/' + self.listprobes[probe] + "/w1_slave"


class Probe:

    """Abstracts class which represents the DS18B20 and DHT22 probes"""

    def __init__(self, idt, settings):
        idt = idt
        settings = dict(settings)
        self.set_settings(settings)
        if idt is not None:
            self.set_id(idt)
        if not self.get_slug():
            self.set_slug(idt)
        self.temperature = ""

    def __str__(self):
        return self.get_id()

    def set_settings(self, settings):
        self.settings = settings

    def has_config(self, materials):
        """
        Tests if the config file exist and has been filled

        :param materials: a configured list of materials (the materials data must be getted first)
        :type materials: Materials

        :return: indicates if the config file exist with attributes
        :rtype: bool

        """
        if materials.get_probe_by_id(self.get_id()) != (None, None):
            return True
        return False

    def get_id(self):
        """
        Gets the id of the probe

        :return: the corresponding id
        :rtype: str
        """
        return self.settings["idt"]

    def set_id(self, idt):
        """set the id of the probe
        """
        self.settings["idt"] = idt

    def has_alert(self):
        """
        Tests if the config has alert settings

        :return: if the user wants the probe to send alert
        :rtype: bool
        """
        return self.settings["alert"]["bool"]

    def set_alert(self, alert):
        """
        Sets the alert bool

        :param alert: True f you want to power alert system on, false otherwise
        :type alert: bool

        :raises TypeError: if alert is not a booleant
        """
        if not isinstance(alert, bool):
            raise TypeError("alert setting is either True or False")
        self.settings["alert"]["bool"] = True

    def get_max_alert(self):
        """
        Gets the maximum value suported before alert

        :return: the max temperature allowed before alert
        :rtype: float
        """
        return self.settings["alert"]["max"]

    def get_min_alert(self):
        """
        Gets the minimum temp supported before alert

        :return: the min temperature allowed before alert
        :rtype: float
        """

        return self.settings["alert"]["min"]

    def set_max_alert(self, max_alert):
        """
        Sets the maximum temperature before alert

        :param max_alert: the maximum temperature desired before alert
        :type max_alert: float

        :raises TypeError: if the max_alert given is not a float
        """
        if not isinstance(max_alert, float):
            raise TypeError("the temperature is a number")
        self.settings["alert"]["max"] = max_alert

    def set_min_alert(self, min_alert):
        """
        Sets the minimum temperature before alert

        :param min_alert: the minimum temp
        :type min_alert: float

        :raises TypeError: if the value given is not a float
        """
        if not isinstance(min_alert, float):
            raise TypeError("the temperature is a number")
        self.settings["alert"]["min"] = min_alert

    def get_slug(self):
        """
        Gets the pseudo name of the probe

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

    def is_stated(self):
        """
        Tests if the probe has a stating option (thermo/hygro)

        :return: True if it is stated
        :rtype: bool
        """
        return self.settings["stated"]["bool"]

    def set_stated(self, bool_, values=None):
        """
        Sets the thermostats option with the list of thermostats

        :param bool_: True for thermostat option
        :type bool_: bool
        :param values: (optional) the list of different temps/hygros desired if True
        :type values: (optional) list

        :raises TypeError: if bool_ is not a bool or temp/hygro not a list of float
        :raises ValueError: if you choose stat option, you need a list of reference values
        """
        if values is None:
            values = []
        if not isinstance(bool_, bool):
            raise TypeError("Stat option should be a boolean")
        if bool_:
            if not values:
                raise ValueError("the list of values desired is empty")
            for i in range(len(values)):
                if not isinstance(values[i], float):
                    raise TypeError("the values must be a list of float")
            self.settings["stated"]["values"] = values
        self.settings["stated"]["bool"] = bool_

    def get_interval(self):
        """
        Gets the list of time slot for the temps

        :return: the list of the beginning of time slot
        :rtype: list
        """
        return self.settings["stated"]["moment"]

    def set_interval(self, intervals):
        """
        Sets the different time slots by the beginning of each time slot

        :param intervals: start of the time slot with the hour written in this form "%H:%M"
        :type intervals: list

        :raises TypeError: if the number of time slots is different from the number of temperatures
        :raises IndexError: if the time slots are not a list
        :raises ValueError: if the time format is uncorrect
        """
        if not isinstance(intervals, list):
            raise TypeError("the intervals must be a list")
        if len(intervals) != len(self.settings["stated"]["values"]):
            raise IndexError("number of intervals must equal number of values")
        regex = re.compile("^(\d\d):(\d\d)$")
        for moment in intervals:
            result = regex.match(moment)
            if not result:
                raise ValueError("the format is uncorrect, use HH:MM")
            hour = int(result.groups()[0])
            minute = int(result.groups()[1])
            if hour > 23 or hour < 0 or minute < 0 or minute > 59:
                raise ValueError("A correct time must be given")
        self.settings["stated"]["moment"] = intervals

    def get_creneau(self):
        """
        Returns the number of time slots

        :return: number of time changing fror a thermostat
        :rtype: int
        """
        return len(self.settings["stated"]["moment"])

    def link_moment_value(self):
        """
        Associates a temp with a moment

        :return: {time_slot_temp: beginning_of_time_slot}
        :rtype: dict
        """
        thermorange = {}
        for i in range(self.get_creneau()):
            thermorange[self.settings["stated"]["moment"][i]] = self.settings[
                "stated"]["values"][i]
        return thermorange

    def get_temperature(self, line=None):
        """
        Abstract method for getting temperature. Line is used only in trhe case of a DS18B20

        :param line: (optional) line of the file which contains the temp
        :type line: str

        :return: the read temperature
        :rtype: float
        """
        return self.temperature



class Ds18b20(Probe):

    def __init__(self, idt=None, settings=None):
        if settings is None:
            global SETTINGS
            settings = dict(SETTINGS)
        sets = settings
        super().__init__(idt, sets)

    def is_thermostated(self):
        return super().is_stated()

    def set_thermostated(self, bool_, values=None):
        return super().set_stated(bool_, values)

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

    def get_temperature(self, line=None):
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
        if temp == []:
            raise EnvironmentError("The probe is detected but not working")
        self.temperature = temp[0] + temp[1] + "." + temp[2]
        return self.temperature


class Dht22(Probe):
    """
    Represents the DHT22 probes. The id of a dht22 correspond to its pin making it easily replaceable
    """
    DHTSET = SETTINGS
    def __init__(self, idt='21', settings=SETTINGS):
        super().__init__(idt, settings)

        self.sensor = Adafruit_DHT.DHT22

    def get_value(self):
        """
        Gets the read values of a DHT22 probe using the Adafruit API
        """
        self.humidity, self.temperature = Adafruit_DHT.read_retry(self.sensor, self.get_id(), retries=2)
        if self.temperature is None or self.humidity is None:
            raise EnvironmentError("The DHT22 probe is not functional")

    def get_temperature(self, line=None):
        return round(self.temperature, 1)

    def get_humidity(self):
        return round(self.humidity, 1)

    def is_hygrostated(self):
        return super().is_stated()

    def set_hygrostated(self, bool_, values=None):
        return super().set_stated(bool_, values)

