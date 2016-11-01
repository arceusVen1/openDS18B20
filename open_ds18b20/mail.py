#!/usr/bin/python3

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Mail():

    def __init__(self):
        self.credentials = {"email": "", "password": ""}
        self.msg = MIMEMultipart()
        self.body = ""
        return

    def sendMail(self, smtp_server="smtp.gmail.com", port=587):
        self.msg.attach(MIMEText(self.body, 'plain'))
        text = self.msg.as_string()
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(self.credentials["email"], self.credentials["password"])
        server.sendmail(self.msg["From"], self.msg["To"], text)
        server.quit()
        return

    def messageBody(self, temperatures, additional="", alert=False):
        if alert:
            self.body = ("An alert has been detected, "
                         "you should check your temperatures\n" + additional)
        else:
            self.body = "Here is the list of the mesured temperatures\n"
        if len(temperatures) > 0:
            for i in range(len(temperatures)):
                self.body += ("probe " + str(i + 1) +
                              " : " + temperatures[i] + "*C\n")
        return self.body

    def messageBuilder(self, toaddr, fromaddr, subject):
        self.msg["From"] = fromaddr
        self.msg["To"] = toaddr
        self.msg["Subject"] = subject
        return self.msg
