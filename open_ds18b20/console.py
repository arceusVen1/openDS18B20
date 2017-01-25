"""
TODO:
    - check if credentials are needed in case of no alert
    - make a function for registering a new probe
"""
import sys
import getpass

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
    settings = {"email": "", "password": "", "number": False, "alert": False}
    sys.stdout.write("What is the number of probes attached ?\n")
    while not settings["number"]:
        try:
            number = int(input(PROMPT))
            if 15 > number >= 0:
                settings["number"] = number
        except:
            sys.stdout.write("a number please !")
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

    sys.stdout.write("woud you like to set an alert system ?(y/n)\n")
    alert = input(PROMPT)
    if str(alert) == "y":
        settings["alert"] = True
    else:
        settings["alert"] = False
    return settings


def config_probe(listprobes):
    configured = []
    unconfigured = []
    for probe in listprobes:
        if probe.has_config():
            probe.get_data()
            configured.append(probe)
        else:
            unconfigured.append(probe)
    display("Already configured probes :")
    for i in range(len(configured)):
        display(str(i) + " - " + configured[i].get_slug())
    display("Unconfigured probes")
    for j in range(len(unconfigured)):
        display(str(i + j) + " - " + unconfigured[j].get_slug())
    display("Please type in a number for the probes to configure :")
    number = int(input(PROMPT))
    if number > i:
        probe = unconfigured[number - i]
    else:
        probe = configured[i]
        display(probe.get_slug())
        if probe.has_alert():
            display("max :" + str(probe.get_max_alert()))
            display("min :" + str(probe.get_min_alert()))
        if probe.is_thermostated():
            display(probe.get_moment())
            display(probe.link_moment_temp())
    display("pseudo ?")
    probe.set_slug(input(PROMPT))
    display("Alert ? (y/n)")
    alert = input(PROMPT)
    if alert == "y":
        probe.set_alert(True)
        display("max ?")
        probe.set_max_alert(float(input(PROMPT)))
        display("min ?")
        probe.set_min_alert(float(input(PROMPT)))
    display("thermostat ? (y/n)")
    thermostat = input(PROMPT)
    if thermostat == "y":
        temps = []
        esc = None
        while esc is None:
            display("add a temp (0 to esc)")
            temp = float(input(PROMPT))
            if temp == 0 and temps != []:
                esc = 0
            else:
                temps.append(temp)
                print(temps)
        probe.set_thermostated(True, temps)
        display("Please give the start of each time lapse in order (HH:MM)")
        moments = []
        for i in temps:
            moments.append(input(PROMPT))
        probe.set_moment(moments)
    probe.set_data()
    for probe in configured:
        probe.config.close_file()
