#!/usr/bin/python3

import smtplib
import psutils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Mail():

    def __init__(self):
        self.credentials = {"email": "", "password": ""}
        self.msg = MIMEMultipart()
        self.body = ""
        return

    def sendMail(self, smtp_server="smtp.gmail.com", port=587):
        sent = False
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
        except:
            pass
        return sent

    def messageBody(self, temperatures, additional="", alert=False):
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
        self.body += str((psutils.virtual_memory().available/psutils.virtual_memory().total))*100
        self.body += "\ncpu usage: "
        self.body += str(psutils.cpu_percent()) + "\n"
        return self.body

    def messageBuilder(self, toaddr, fromaddr):
        self.msg["From"] = fromaddr
        self.msg["To"] = toaddr
        return self.msg
