import sys
import getpass

# GLOBAL--------------------------------------------------

PROMPT = '> '

# ---------------------------------------------------------


class Console(object):
    """display all the needed info in the console"""

    def __init__(self):
        return

    def display(self, string):
        sys.stdout.write(str(string) + "\n")

    def writeDependencies(self):
        """indicates what to do if you don't have the modules installed


        Returns:
            bool: just to know that you miss the modules
        """
        sys.stdout.write("before continuing you should add "
                         "\"w1-gpio\" & \"w1-therm\" to /etc/modules files\n")
        return False

    def promptConfig(self, settings):
        """ask for the new config settings

        Args:
            config (ConfigFile): File to write the config

        Returns:
            none: The configuration has been saved
        """
        sys.stdout.write(
            "adress where emails are going to be send and sent from ?\n")
        settings["email"] = input(PROMPT)
        sys.stdout.write("password ? "
                         "(WARNING the password will be clear in the config file)\n")
        # to hide the password in the console
        settings["password"] = getpass.getpass()
        sys.stdout.write("What is the number of probes attached ?\n")
        try:
            settings["number"] = int(input(PROMPT))
        except:
            sys.stdout.write("a number please !")
        sys.stdout.write("woud you like to set an alert system ?(y/n)\n")
        alert = input(PROMPT)
        if str(alert) == "y":
            settings["alert"]["choice"] = True
            sys.stdout.write("max temp ?\n")
            settings["alert"]["max"] = int(input(PROMPT))
            sys.stdout.write("min temp ?\n")
            settings["alert"]["min"] = int(input(PROMPT))
        return settings
