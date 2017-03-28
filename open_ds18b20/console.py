"""
TODO:
    - check if credentials are needed in case of no alert
    - make a function for registering a new probe
"""
import sys
import getpass
import open_ds18b20.probe

# GLOBAL--------------------------------------------------

PROMPT = '> '


# ---------------------------------------------------------


def display(string):
    sys.stdout.write(str(string) + "\n")


def write_dependencies():
    """
    Indicates what to do if you don't have the modules installed
    """
    sys.stdout.write("before continuing you should add "
                     "\"w1-gpio\" & \"w1-therm\" to /etc/modules files\n")


def prompt_config():
    """
    Asks for the new config settings
    """
    settings = {"email": "", "password": "", "DS18B20": 0, "DHT22": 0, "alert": False}
    sys.stdout.write("What is the number of DS18B20 probes attached ?\n")
    while not settings["DS18B20"]:
        try:
            number = int(input(PROMPT))
            if 15 > number >= 0:
                settings["DS18B20"] = number
        except:
            sys.stdout.write("a number please !")
    sys.stdout.write("What is the number of DHT22 probes attached ?\n")
    while not settings["DHT22"]:
        try:
            number = int(input(PROMPT))
            if 2 > number >= 0:
                settings["DHT22"] = number
        except:
            sys.stdout.write("a number please !")
    sys.stdout.write("woud you like to set an alert system ?(y/n)\n")
    alert = input(PROMPT)
    if str(alert) == "y":
        settings["alert"] = True
    else:
        settings["alert"] = False
    sys.stdout.write(
        "adress where emails are going to be send and sent from ?\n")
    settings["email"] = input(PROMPT)
    sys.stdout.write("password ? "
                     "(WARNING the password will be clear in the config file)\n")
    # to hide the password in the console
    settings["password"] = getpass.getpass()
    return settings


def config_probe(listprobes, materials):
    """
    Using the probe command from command line,
    shows the config of the attached probes and can configure them

    :param listprobes: list of probes from Probe class
    :type listprobes: list
    """
    configured = []
    unconfigured = []
    for dht22 in materials.get_dht22():
        configured.append(open_ds18b20.probe.Dht22(settings=dht22))
    for probe in listprobes:
        if probe.has_config(materials):
            configured.append(probe)
        else:
            unconfigured.append(probe)
    nc = len(configured)
    nu = len(unconfigured)
    display("Sondes déjà configurées :")
    for i in range(nc):
        display(str(i) + " - " + configured[i].get_slug())
    display("Sondes non-configurées attachées")
    for j in range(nu):
        display(str(nc + j) + " - " + unconfigured[j].get_slug())
    # create a new instance of Dht22
    display(str(nc + nu) + " - nouvelle DHT22")
    unconfigured.append(open_ds18b20.probe.Dht22())
    display("Veuillez entrer un numéro afin d'effectuer une action (ctrl-C pour sortir) :")
    number = int(input(PROMPT))
    if number >= nc:
        probe = unconfigured[number - nc]
    else:
        probe = configured[number]
        display(probe.get_slug())
        if probe.has_alert():
            display("max :" + str(probe.get_max_alert()))
            display("min :" + str(probe.get_min_alert()))
        if probe.is_stated():
            display(probe.get_interval())
            display(probe.link_moment_value())
    flag = False
    while not flag:
        display("pseudo ?")
        try:
            probe.set_slug(input(PROMPT))
            flag = True
        except Exception as e:
            display(str(e))
    flag = False
    display("Alerte ? (o/)")
    alert = input(PROMPT)
    if alert == "o":
        probe.set_alert(True)
        while not flag:
            display("max ?")
            try:
                probe.set_max_alert(float(input(PROMPT)))
                flag = True
            except Exception as e:
                display(str(e))
        flag = False
        while not flag:
            display("min ?")
            try:
                probe.set_min_alert(float(input(PROMPT)))
                flag = True
            except Exception as e:
                display(str(e))
    flag = False
    display("thermostat (DS18B20) /hygrostat (DHT22) ? (o/n)")
    stat = input(PROMPT)
    if stat == "o":
        while not flag:
            try:
                values = []
                esc = None
                while esc is None:
                    display("Ajouter une température (DS18B20)/seuil d'humidité (DHT22) (0 = esc)")
                    value = float(input(PROMPT))
                    if value == 0 and values != []:
                        esc = 0
                    else:
                        values.append(value)
                        print(values)
                probe.set_stated(True, values)
                flag = True
            except Exception as e:
                display(str(e))
        flag = False
        while not flag:
            display("Veuillez entrer le départ de chaque créneau horaire (HH:MM)")
            moments = []
            try:
                for i in values:
                    moments.append(input(PROMPT))
                    print(moments)
                probe.set_interval(moments)
                flag = True
            except Exception as e:
                display(str(e))
    materials.add_probe(probe)
    materials.set_data()
    materials.config.close_file()
