#!/usr/bin/python3
import sys
import open_ds18b20.fichier as f
from open_ds18b20.mail import Mail
from open_ds18b20.probe import Materials, Ds18b20, Dht22
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
    config.set_ds18b20(settings["DS18B20"])
    config.set_dht22(settings["DHT22"])
    config.set_alert(settings["alert"])
    config.set_data()


def probe_conf_command(probes, materials):
    """
    Shows every configured and unconfigured probes detected and
    allow the user to configure and see the config of every of them

    :param materials: configuration of all the probes
    :type materials: Materials
    :param probes: list of probes from Probe class
    :type probes: list
    """
    config_probe(probes, materials)


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
    humidity = {}
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
    # get the data from materials
    materials.allow_config()
    materials.get_data()
    # detect the probes attach
    materials.detect_attached_probes()
    # get all the probes attach
    probes = []
    print(materials.listprobes)
    print(materials.listPaths)
    for idProbe in materials.listprobes:
        # test the presence of the probe
        fprobe = materials.get_ds18b20_by_id(idProbe)
        print(idProbe)
        print(fprobe)
        if fprobe[0]:
            p = Ds18b20(idt=idProbe, settings=fprobe[0])
            probes.append(p)
        else:
            p = Ds18b20(idt=idProbe)
            print(p)
            probes.append(p)
    print(locals())
    print(str(probes[0]), str(probes[1]))
    # if the probe command is used
    if probe_conf:
        probe_conf_command(probes, materials)
    # number of DS18B20 probes attached
    number = config.get_ds18b20() + config.get_dht22()
    # try to read the probes temp
    try:
        for probe in probes:
            # put the file probe in files
            fichier = f.ProbeFile(materials.listPaths[probe.get_id()])
            print(fichier)
            files.append(fichier)
            # test the probe
            if probe.is_working(fichier.read_line(1)):
                # the probe is working
                materials.num_working_probes += 1
                print(probe.get_slug())
                templine = fichier.read_line(2)
                probe.get_temperature(templine)
                temperatures[probe.get_slug()] = float(probe.temperature)
    # append an exception message if exception is raised
    except Exception as e:
        print(e)
        messages.append("* temperatures *couldn't be read")
    # DHT22 reading
    for dht22 in materials.get_dht22():
        dht22 = Dht22(settings=dht22)
        try:
            dht22.get_value()
            temperatures[dht22.get_slug()] = dht22.get_temperature()
            humidity[dht22.get_slug()] = dht22.get_humidity()
            # include the dht22 probes for alert reading
            probes.append(dht22)
            materials.num_working_probes += 1
        except EnvironmentError:
            messages.append("*one DHT22 not *****detected****")
    # if not all of the probes attached are working
    if materials.num_working_probes < number:
        difference = number - materials.num_working_probes
        messages.append("* " + (str(difference) +
                                " probes not **** detected ***"))
    # if alert compare the max/min with real temp
    if len(temperatures) > 0 or len(humidity) > 0:
        for p in range(materials.num_working_probes):
            if probes[p] in temperatures and probes[p].has_alert():
                # test if alert for temperature
                if isinstance(probes[p], Ds18b20) and (
                                temperatures[probes[p].get_slug()] >= probes[p].get_max_alert() or temperatures[
                            probes[p].get_slug()] <= probes[p].get_min_alert()):
                    messages.append(probes[p].get_slug() + " : too high/low temperature")
                # test if alert for humidity
                elif isinstance(probes[p], Dht22) and (
                                humidity[probes[p].get_slug()] >= probes[p].get_max_alert() or humidity[
                            probes[p].get_slug()] <= probes[p].get_min_alert()):
                    messages.append(probes[p].get_slug() + " : too high/low humidity")
    # if messages list is not empty, there is an a least one alert
    if len(messages) > 0:
        alert = True
    # to force a mail message with the optional argument "mail"
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
    return temperatures, humidity, messages


if __name__ == '__main__':
    main()
