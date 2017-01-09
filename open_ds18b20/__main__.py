#!/usr/bin/python3
import sys
from open_ds18b20.fichier import File, ConfigFile, ProbeFile, ModuleFile
from open_ds18b20.mail import Mail
from open_ds18b20.probe import Materials, Probe


def argGestion(args):
    erase = False
    mail = False
    for i in range(len(args)):
        if args[i] == "erase":
            erase = True
        elif args[i] == "mail":
            mail = True
    return erase, mail

# def test(probe):
   # probe.allow_config()
   # probe.set_idt()
   # probe.set_slug("test")
   # probe.set_alert(True)
   # probe.set_max_alert(25)
   # probe.set_min_alert(24)
   # probe.set_data()
   # return


def createMail(temperatures, config, alert=False, messages=[]):
    """create the email to use it more easily on the __main__

    Args:
        temperatures (list): List of temperatures
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
    email.messageBody(temperatures, message, alert)
    email.credentials["email"], email.credentials[
        "password"] = config.get_credentials()
    email.messageBuilder(email.credentials["email"],
                         email.credentials["email"])
    sent = email.sendMail()
    return sent


def main():
    # initialize the returned instance
    temperatures = {}
    messages = []
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
        File("/home/pi/ds18b20_conf/config.json").remove_file()
    # create if needed and open a config file
    config = ConfigFile("/home/pi/ds18b20_conf/config.json")
    # if the config file is empty (especially if it has just been created)
    if config.nbline == 0:
        # ask for the new settings in the console
        config.set_settings()
    # read the data now that you should have some
    config.read_data()
    # create a Probe instance
    materials = Materials()
    # detect the probes attach
    materials.detectProbes()
    # get all the probes attach
    probes = []
    n = len(materials.listprobes)
    for idProbe in materials.listprobes:
        probes.append(Probe(idProbe))
# dht_h, dht_t = dht.read_retry(dht.DHT22,17)
    number = config.get_probes()
    # try to read the probes temp
    try:
        for p in range(n):
            # put the file probe in files
            files.append(ProbeFile(materials.listPaths[p]))
            # test the probe
            if probes[p].is_working(files[p].read_line(1)):
                if probes[p].has_config():
                    probes[p].get_data()
                # the probe is working
                materials.numWorkingProbes += 1
                templine = files[p].read_line(2)
                probes[p].getTemperature(templine)
                temperatures[probes[p].get_slug()] = float(probes[
                    p].temperature)
    # append an exception message if exception is raised
    except:
        messages.append("* temperatures *couldn't be read")
    # if not all of the probes attached are working
    if materials.numWorkingProbes < number:
        difference = number - materials.numWorkingProbes
        messages.append("* " + (str(difference) +
                                          " probes not **** detected ***"))
    # if alert compare the max/min with real temp
    if len(temperatures) > 0:
        for p in range(materials.numWorkingProbes):
            if probes[p].has_alert():
                if (temperatures[probes[p].get_slug()] >= probes[p].get_max_alert() or
                        temperatures[probes[p].get_slug()] <=
                        probes[p].get_min_alert()):
                    messages.append(probes[p].get_slug() +
                                              " : too high/low temperature")
    # test if there is any alert to display
    if len(messages) > 0:
        alert = True
    # to force a mail message with the optionnal argument "mail"
    if mail or alert:
        sent = createMail(temperatures,
                          config, alert, messages)
        if not sent:
            messages.append("mail couldn't be***** send *****")
        # sys.exc_info()[:2]
    # close the opened file
    for i in range(len(files)):
        files[i].close_file()
    config.close_file()
    return temperatures, messages


if __name__ == '__main__':
    main()
