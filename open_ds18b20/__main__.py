#!/usr/bin/python3
import sys
import open_ds18b20.fichier as f
from open_ds18b20.mail import Mail
from open_ds18b20.probe import Materials, Probe
from open_ds18b20.console import *


def arg_gestion(args):
    """
    Checks the option given in the command line

    :return erase: erase option
    :rtype erase: bool
    :return mail: mail option
    :rtype mail: bool
    :return new: new option
    :rtype new: bool
    """
    erase = False
    mail = False
    config = False
    probe = False
    for i in range(len(args)):
        if args[i] == "erase":
            erase = True
        elif args[i] == "mail":
            mail = True
        elif args[i] == "new":
            config = True
        elif args[i] == "probe":
            probe = True
    return erase, mail, config, probe


def erase_command():
    """
    Erases a file if required, used with erase option

    """
    f.File("/home/pi/ds18b20_conf/config.json").remove_file()


def config_command(config):
    """
    Asks for the new settings config, used with "new" option

    :param config: the config file where the settings are to be registered
    :type config: ConfigFile
    """
    settings = prompt_config()
    config.set_credentials(settings["email"], settings["password"])
    config.set_probes(settings["number"])
    config.set_alert(settings["alert"])
    config.set_data()


def probe_conf_command(probes):
    """
    Shows every configured and unconfigured probes detected and
    allow the user to configure and see the config of every of them
    """
    config_probe(probes)


def create_mail(temperatures, config, alert=False, messages=None):
    """
    Creates a mail and send it using the Mail class functions

    :param temperatures: {"probe_slug": temp (float)}
    :type temperatures: dict
    :param config: The config.json file
    :type config: ConfigFile
    :param alert: (optional) set to False by default
    :type alert: bool
    :param messages: (optional) empty unless alert = True
    :type messages: list

    :return: sent to indicates if the messages is sent
    :rtype: bool
    """
    if messages is None:
        messages = []
    email = Mail()
    message = ""
    for i in range(len(messages)):
        message += str(messages[i])
        message += "\n"
    email.message_body(temperatures, message, alert)
    email.credentials["email"], email.credentials[
        "password"] = config.get_credentials()
    email.message_builder(email.credentials["email"],
                          email.credentials["email"])
    sent = email.send_mail()
    return sent


def main():
    # initialize the returned instance
    temperatures = {}
    messages = []
    # flag for the alert
    alert = False
    # test that the moduels are present
    tester = f.ModuleFile("/etc/modules").tester()
    if not tester:
        write_dependencies()
        return
    files = []
    # test the presences of an argument
    erase, mail, general_conf, probe_conf = arg_gestion(sys.argv)
    # if erase arg the config is reset
    if erase:
        # erase the config file to avoid conflict
        erase_command()
    # create if needed and open a config file
    config = f.ConfigFile("/home/pi/ds18b20_conf/config.json")
    # if the "new" option is given
    if general_conf:
        # ask for the new config
        config_command(config)
        return
    # if the config file is empty (especially if it has just been created)
    if config.nbline == 0:
        # ask for the new settings in the console
        display("the config file is empty, use 'new' option")
        return

    # read the data now that you should have some
    config.get_data()
    # create a Probe instance
    materials = Materials()
    # detect the probes attach
    materials.detect_probes()

    # get all the probes attach
    probes = []
    n = len(materials.listprobes)
    for idProbe in materials.listprobes:
        probes.append(Probe(idProbe))
    if probe_conf:
        probe_conf_command(probes)
    # dht_h, dht_t = dht.read_retry(dht.DHT22,17)
    number = config.get_probes()
    # try to read the probes temp
    try:
        for p in range(n):
            # put the file probe in files
            files.append(f.ProbeFile(materials.listPaths[p]))
            # test the probe
            if probes[p].is_working(files[p].read_line(1)):
                if probes[p].has_config():
                    probes[p].get_data()
                # the probe is working
                materials.numWorkingProbes += 1
                templine = files[p].read_line(2)
                probes[p].get_temperature(templine)
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
            if probes[p].has_alert() and (
                            temperatures[probes[p].get_slug()] >= probes[p].get_max_alert() or temperatures[
                        probes[p].get_slug()] <= probes[p].get_min_alert()):
                # test if there is any alert to display
                messages.append(probes[p].get_slug() +
                                " : too high/low temperature")
    # if messages list is not empty, there is an a least one alert
    if len(messages) > 0:
        alert = True
    # to force a mail message with the optionnal argument "mail"
    if mail or alert:
        sent = create_mail(temperatures,
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
