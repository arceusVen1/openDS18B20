#!/usr/bin/python3

import smtplib
import psutil
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Mail:

    """
    Deals with a mail creation from a gmail address.
    A mail address must accept the "low security usage" to allow python to send a mail from it
    """

    def __init__(self):
        self.credentials = {"email": "", "password": ""}
        self.msg = MIMEMultipart()
        self.body = ""
        return

    def send_mail(self, smtp_server="smtp.gmail.com", port=587):
        """
        Sends the mail built

        :param smtp_server: (optional, smtp.gmail.com by default) the smtp server to send the mail
        :type smtp_server: str
        :param port: (optional, 587 by default) the server ports
        :type port: int
        :return: if the mail has been sent
        :rtype: bool
        """
        try:
            self.msg.attach(MIMEText(self.body, 'plain'))
            text = self.msg.as_string()
            server = smtplib.SMTP(smtp_server, port)
            server.starttls()
            server.login(self.credentials["email"],
                         self.credentials["password"])
            server.sendmail(self.msg["From"], self.msg["To"], text)
            server.quit()
            sent = True
        except Exception as e:
            sent = False
            print("the message could not be sent :", e)
        return sent

    def message_body(self, temperatures, additional=None, alert=False):
        """
        Creates the body of the email

        :param temperatures: {probe_name: temp}
        :type temperatures: dict
        :param additional: (optional) any additional messages to send
        :type additional: str
        :param alert: (optional, False by default) if the mail is defined as an alert
        :type alert: bool

        :return: the body of the mail and its subject
        :rtype: str

        :Example:

            subject: List of temperatures
            body:   Here is the list of the mesured temperatures
                    probe_name : temp
                    ...
                    probe_name : temp
                    memory usage: x%
                    cpu usage: x%
        """
        if additional is None:
            additional = ""
        if alert:
            self.msg["Subject"] = "Alert Detected"
            self.body = ("An alert has been detected, "
                         "you should check your temperatures\n" + additional)
        else:
            self.msg["Subject"] = "List of Temperatures"
            self.body = "Here is the list of the mesured temperatures\n"
        if len(temperatures) > 0:
            for probe, temp in temperatures.items():
                self.body += (str(probe) +
                              " : " + str(temp) + "*C\n")
        self.body += "\nmemory usage: "
        self.body += str((round(psutil.virtual_memory().available/psutil.virtual_memory().total)))*100 + "%"
        self.body += "\ncpu usage: "
        self.body += str(psutil.cpu_percent()) + "%" + "\n"
        return self.body

    def message_builder(self, to_addr, from_addr):
        """
        Defines the address to send the mail from and to

        :param to_addr: address to send mail to
        :type to_addr: str
        :param from_addr: address to send mail from (must accept "low security usage"
        :type from_addr: str
        """
        self.msg["From"] = from_addr
        self.msg["To"] = to_addr
