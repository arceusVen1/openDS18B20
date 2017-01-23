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
    settings = {}
    sys.stdout.write("What is the number of probes attached ?\n")
    while not settings["number"]:
        try:
            number = int(input(PROMPT))
            if number < 15 and number >= 0:
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


def config_probe():
    pass
