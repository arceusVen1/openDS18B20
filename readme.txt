I am working on this project to help people with the automation of the task of reading temperatures with DS18B20 probe on a Raspberry Pi 3

How to use OpenDS18B20 ?

This program runs under pyhton 2.7

Before anything you should create a random gmail adress used only for the purpose of this sofware where you enable the low security usage to allow python to send email from this specific adress you just created (you can easily find how to do this by googling it ;)

It is then very easy to use ! Once installed (sudo pyhton setup.py install) you just need to use the open_ds18b20 command to start it. The first start of the software will create a config.json file and ask for an adress email as well as a password for it. This can manually modified later of course by running the program with the optional argument "erase". For now it only works with gmail adresses and will send the emails from this adress and receive them there as well. Feel free to modify the code in mail.py to configure the software for an another email adress domain (you will need to change the default smtp server or modify the __main__.py and give the smtp server you want as an argument of the sendMail() function). 
Before using this sofware, make sure you have properly modified the "/etc/modules" file by adding "w1-gpio" and "w1-therm" and have then rebooted your RPi (IT'S ETREMELY IMPORTANT). The sofware will tell you anyway if you haven't.

I am still working on this project and it needs yet a proper installer as well as a good documentation. I am only a student so I am still improving, any help or advice will be glady acceted as well as feedback :)

Feel free to use this program wherever and whenever you desire and modify it as much as you like :D




