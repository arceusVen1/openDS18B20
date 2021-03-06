#!/usr/bin/python3

import json
import os
import re

SETTINGS = {"email": "", "password": "", "DS18B20": 0, "DHT22": 0, "alert": False}


class File:

    """abstract class of file"""

    def __init__(self, filepath):
        self.path = filepath
        self.file = open(self.path, "r")
        self.content = list(self.file)
        self.nbline = len(self.content)

    def read_line(self, nb_line):
        """
        Reads a specific line

        :param nb_line: number of the line (human format, starting from line 1)
        :type nb_line: int

        :return: the content read
        :rtype: str
        """
        return self.content[nb_line - 1]

    def close_file(self):
        """
        Closes a file
        """
        self.file.close()

    def remove_file(self):
        """
        Removes the file from the system
        """
        self.close_file()
        os.remove(self.path)

    def _save(self, element):
        """
        Overwrite text in a file to ensure that the file have been saved
        :param element: what needs to be written
        :type element: int, float, str, dict, list ...
        """
        self.file = open(self.path, "w")
        self.file.write(element)
        self.file.close()
        self.file = open(self.path, "r")

    def exists(self):
        """
        Checks if the file exists at the given path

        :return: True if the file exists, False otherwise
        :rtype: bool
        """
        if os.path.exists(self.path):
            return True
        return False

    def create(self):
        """
        Creates a file at the given path
        """
        try:
            os.mknod(self.path)
        except OSError:
            pass

    def __str__(self):
        return self.path


class ConfigFile(File):

    """Deal with the configuration file in /home/pi/ds18b20_conf/config.json, inherits from File"""

    def __init__(self, filepath):
        """
        Initiated with the file path, it will check for the existence and create it if necessary.
        The file will then be opened and listed

        :param filepath: absolute file path
        :type filepath: str
        """
        self.path = filepath
        self.settings = SETTINGS
        os_path = os.path.abspath(self.path)
        if not os.path.exists(os_path):
            dirpath = os.path.dirname(os_path)
            print("creating config.json in " + str(dirpath))
            try:
                os.makedirs(dirpath)
            except OSError:
                print("already existing folder")
                self.create()
        self.file = open(self.path, 'r')
        self.content = list(self.file)
        self.nbline = len(self.content)

    def get_data(self):
        """
            Loads the actual settings from the probe_config file

            :return: the new settings
            :rtype: dict
        """
        self.file.seek(0)
        self.settings = json.load(self.file)
        return self.settings

    def set_data(self):
        """
        Overwrites the settings configuration of config.json
        WARNING: once your settings are all set, this function must be called to save them
        """
        self.register()

    def get_credentials(self):
        """
        Gets the credential from the json loaded data

        :return: email and password from the data
        :rtype: str
        """
        email = self.settings["email"]
        password = self.settings["password"]
        return email, password

    def set_credentials(self, email, password):
        """
        Registers in the settings the credentials

        :param email: email adress to send to and from
        :type email: str
        :param password: the password of the above adress (warning ! kept clear)
        :type password: str

        :raises TypeError: if the email or password are not strings
        """
        if not isinstance(email, str) or not isinstance(password, str):
            raise TypeError("email and password are strings")
        self.settings["email"] = email
        self.settings["password"] = password

    def get_ds18b20(self):
        """
        Gets the number of DS18B20 probes that should be attached to the system

        :return: the number of DS18B20 probes theoretically attached to the system (< 15)
        :rtype: int
        """
        return int(self.settings["DS18B20"])

    def get_dht22(self):
        """
        Gets the number of DHT22 probes that should be attached to the system

        :return: the number of DHT22 probes theoretically attached to the system (< 15)
        :rtype: int
        """
        return int(self.settings["DHT22"])

    def set_ds18b20(self, number):
        """
        Registers the number of DS18B20 probes attached to the system (< 15)

        :param number: the number of DS18B20 probes attached
        :type number: int

        :raises TypeError: if number is not a int
        """
        if not isinstance(number, int):
            raise TypeError("the number of probe must be an integer")
        self.settings["DS18B20"] = number

    def set_dht22(self, number):
        """
        Registers the number of DHT22 probes attached to the system (< 15)

        :param number: the number of DHT22 probes attached
        :type number: int

        :raises TypeError: if number is not a int
        """
        if not isinstance(number, int):
            raise TypeError("the number of probe must be an integer")
        self.settings["DHT22"] = number

    def has_alert(self):
        """
        Checks if an alert system is enabled

        :return: True if alert system is enabled, false otherwise
        :rtype: bool
        """
        if self.settings["alert"]:
            return True
        return False

    def set_alert(self, alert):
        """
        Enables/disables the alert system

        :param alert: True for enabling, False for disabling
        :type alert: bool

        :raises TypeError: if alert is not a bool
        """
        if not isinstance(alert, bool):
            raise TypeError("alert option must be a bool")
        self.settings["alert"] = alert

    def register(self):
        """
        Registers the (new) settings in the config file by overwriting the file
        """
        element = json.dumps(self.settings, indent=4)
        self._save(element)


class ProbeConfigFile(ConfigFile):
    """deals with the config file of the probes"""

    def __init__(self, path):
        """
        Class constructor, only turns a path string in a os path.
        Since a probe does not necessarily have a config file yet, you don't want to create it automatically.
        That's why there is no call to super class

        :param path: absolute path of the config file
        :type path: str
        """
        # super(ProbeConfigFile, self).__init__()
        self.path = os.path.abspath(path)

    def edit(self):
        """
        If the file exists, use this function to read it
        """
        self.file = open(self.path, "r")
        self.content = list(self.file)
        self.nbline = len(self.content)


class ProbeFile(File):

    """Deals with the file generated by the connected probes"""

    def __init__(self, filepath):
        super(ProbeFile, self).__init__(filepath)


class ModuleFile(File):

    """Deals with the file /etc/modules"""

    def __init__(self, filepath):
        super(ModuleFile, self).__init__(filepath)

    def tester(self):
        """
        Tests the presence w1-therm and w1-gpio modules in the /etc/modules

        :return: True if the modules are installed, false otherwise
        :rtype: bool
        """
        flag = [False, False]
        for i in range(self.nbline):
            line = self.read_line(i + 1)
            if re.match(r"^w1-gpio", line):
                flag[0] = True
            if re.match(r"^w1-therm", line):
                flag[1] = True
        if flag != [True, True]:
            return False
        else:
            return True
