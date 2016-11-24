#!/usr/bin/python3
import sys
import os
import re
import getpass
import time
import subprocess
from open_ds18b20 import fichier, mail, probe


# GLOBAL--------------------------------------------------

SETTINGS = {"email": "", "password": "", "number": 0,
            "alert": {"choice": False, "max": 0, "min": 0}}
PROMPT = '> '

# ---------------------------------------------------------


def to_float(array):
    """turn a list's integer in float (for python2)

    Args:
        array (list): array of number

    Returns:
        list: the same array with float numbers
    """
    floater = []
    for i in range(len(array)):
        floater.append(float(array[i]))
    return floater


def initialConfig():
    """try to open the config file or creates one if there's not

    Returns:
        ConfigFile: the opened config.json file
    """
    path = "/home/pi/ds18b20_conf"
    try:
        os.path.abspath(path)
        config = fichier.ConfigFile(path + "/config.json")
    except IOError:
        print("creating config.json in " + path)
        try:
            os.makedirs(path)
        except OSError:
            print("already existing folder")
        subprocess.Popen(["touch", path + "/config.json"])
        # leaves enough time for the subprocess to create the file
        time.sleep(1)
        config = fichier.ConfigFile(path + "/config.json")
    return config


def writeDependencies():
    """indicates what to do if you don't have the modules installed


    Returns:
        bool: just to know that you miss the modules
    """
    print("before continuing you should add "
          "\"w1-gpio\" and \"w1-therm\" to /etc/modules files")
    return False


def promptConfig(config):
    """ask for the new config settings

    Args:
        config (ConfigFile): File to write the config

    Returns:
        none: The configuration has been saved
    """
    print("adress where emails are going to be send and sent from ? ")
    SETTINGS["email"] = input(PROMPT)
    print("password ? "
          "(warning the password will be kept clear in the config file)")
    # to hide the password in the console
    SETTINGS["password"] = getpass.getpass()
    print("What is the number of probes attached ?")
    try:
        SETTINGS["number"] = int(input(PROMPT))
    except:
        print("a number please !")
    print("woud you like to set an alert system ?(y/n)")
    alert = input(PROMPT)
    if str(alert) == "y":
        SETTINGS["alert"]["choice"] = True
        print("max temp ?")
        SETTINGS["alert"]["max"] = int(input(PROMPT))
        print("min temp ?")
        SETTINGS["alert"]["min"] = int(input(PROMPT))
    config.register(SETTINGS)
    return


def modulesTester():
    """test the presence w1-therm and w1-gpio modules in the /etc/modules

    Returns:
        bool: True if the modules are installed, false otherwise
    """
    flag = [False, False]
    modules = fichier.ModuleFile("/etc/modules")
    for i in range(modules.nbline):
        line = modules.readLine(i + 1)
        if re.match(r"^w1-gpio", line):
            flag[0] = True
        if re.match(r"^w1-therm", line):
            flag[1] = True
    if flag != [True, True]:
        return writeDependencies()
    else:
        return True


def argGestion(args):
    erase = False
    mail = False
    for i in range(len(args)):
        if args[i] == "erase":
            erase = True
        elif args[i] == "mail":
            mail = True
    return erase, mail


def createMail(probes, config, alert=False, messages=[]):
    """create the email to use it more easily on the __main__

    Args:
        probes (Probe): Probe instance
        subject (str): Subject of the message
        config (ConfigFile): Config file
        alert (bool, optional): if it is an alert mail

    Returns:
        bool: indicates if mail has been sent
    """

    email = mail.Mail()
    message = ""
    for i in range(len(messages)):
        message += str(messages[i])
        message += "\n"
    email.messageBody(probes.temperatures, message, alert)
    email.credentials["email"], email.credentials[
        "password"] = config.getCredentials()
    email.messageBuilder(email.credentials["email"],
                         email.credentials["email"])
    sent = email.sendMail()
    return sent


def main():
    # initialize the returned instance
    result = {"temperatures": [], "messages": []}
    # flag for the alert
    alert = False
    # test that the moduels are present
    tester = modulesTester()
    if not tester:
        return
    files = []
    erase, mail = argGestion(sys.argv)
    # if erase arg the config is reset
    if erase:
        # erase the config file to avoid conflict
        os.remove("/home/pi/ds18b20_conf/config.json")
    # create if needed and open a config file
    config = initialConfig()
    # if the config file is empty (especially if it has just been created)
    if config.nbline == 0:
        # ask for the new settings in the console
        promptConfig(config)
    # read the data now that you should have some
    config.readData()
    # create a Probe instance
    probes = probe.Probe()
    # detect the probes attach
    probes.detectProbe()
# dht_h, dht_t = dht.read_retry(dht.DHT22,17)
    number = config.getProbes()
    if len(probes.listprobes) < number:
        difference = number - len(probes.listprobes)
        result["messages"].append("* " + (str(difference) +
                                          " probes not **** detected ***"))
        alert = True
    # try to read the probes temp
    try:
        for p in range(len(probes.listprobes)):
            files.append(fichier.ProbeFile(probes.listprobes[p]))
            templine = files[p].readLine(2)
            probes.getTemperature(templine)
    # append an exception message if exception is raised
    except:
        # , sys.exc_info()[:2]
        result["messages"].append("* temperatures *couldn't be read")
        alert = True
    # transform the temp in float (for python 2)
    floater = to_float(probes.temperatures)
    # if alert compare the max/min with real temp
    if config.has_alert() and len(floater) > 0:
        if (max(floater) >= config.getMaxTempAlert() or
                min(floater) <= config.getMinTempAlert()):
            result["messages"].append("too high/low temperature")
            alert = True
    # to force a mail message with the optionnal argument "mail"
    if mail or alert:
        sent = createMail(probes, config, alert, result["messages"])
        if not sent:
            result["messages"].append("mail couldn't be***** send *****")
        # sys.exc_info()[:2]
    # close the opened file
    for i in range(len(files)):
        files[i].closeFile()
    config.closeFile()
    result["temperatures"] = probes.temperatures
    return result


if __name__ == '__main__':
    main()
