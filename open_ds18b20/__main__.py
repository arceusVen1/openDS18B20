#!/usr/bin/python3
import sys
from open_ds18b20.fichier import File, ConfigFile, ProbeFile, ModuleFile
from open_ds18b20.mail import Mail
from open_ds18b20.probe import Materials, Probe


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

    email = Mail()
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
    tester = ModuleFile("/etc/modules").tester()
    if not tester:
        return
    files = []
    erase, mail = argGestion(sys.argv)
    # if erase arg the config is reset
    if erase:
        # erase the config file to avoid conflict
        File("/home/pi/ds18b20_conf/config.json").removeFile()
    # create if needed and open a config file
    config = ConfigFile("/home/pi/ds18b20_conf/config.json")
    # if the config file is empty (especially if it has just been created)
    if config.nbline == 0:
        # ask for the new settings in the console
        config.set_settings()
    # read the data now that you should have some
    config.readData()
    # create a Probe instance
    materials = Materials()
    # detect the probes attach
    materials.detectProbe()
    # get all the probes attach
    probes = []
    n = len(materials.listprobes)
    for probe in range(n):
        probes.append(Probe(probe))
# dht_h, dht_t = dht.read_retry(dht.DHT22,17)
    number = config.getProbes()
    # try to read the probes temp
    try:
        for p in range(n):
            files.append(ProbeFile(materials.listPaths[p]))
            if probes[p].is_working(files[p].readLine(1)):
                materials.numWorkingProbes += 1
                templine = files[p].readLine(2)
                probes[p].getTemperature(templine)
                result["temperatures"].append(probes[p].temperature)
    # append an exception message if exception is raised
    except:
        # , sys.exc_info()[:2]
        result["messages"].append("* temperatures *couldn't be read")
        alert = True
    if materials.numWorkingProbes < number:
        difference = number - materials.numWorkingProbes
        result["messages"].append("* " + (str(difference) +
                                          " probes not **** detected ***"))
        alert = True
    # transform the temp in float (for python 2)
    floater = to_float(result["temperatures"])
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
