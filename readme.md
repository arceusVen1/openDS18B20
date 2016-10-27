OpenDS18B20
==========

I am working on this project to help people with the automation of the task of reading temperatures with DS18B20 probe on a Raspberry Pi 3

How to use OpenDS18B20 ?

This program runs under python 2.7 for now but will soon be updated in python 3 version


Before anything you should create a random gmail adress used only for the purpose of this sofware where you enable the low security usage to allow python to send email from this specific adress you just created (you can easily find how to do this by googling it ;)

It is then very easy to use ! 
Install it
*********************************************************************

	$ sudo python setup.py install 

*********************************************************************

you just need to use the following command to start it from the console 

*********************************************************************

	$ open_ds18b20 

*********************************************************************

The first start of the software will create a config.json file in /home/pi (feel free to ajust this folder) and ask for an adress email as well as a password for it. 

This can manually modified later of course by running the program :

*********************************************************************

	$ open_ds18b20 erase

*********************************************************************

For now it only works with gmail adresses ! It will send the emails from the same adress where you receive them. 
Feel free to modify the code in mail.py to configure the software for an another email adress domain (you will need to change the default smtp server or modify the __main__.py and give the smtp server you want as an argument of the sendMail() function).

Before using this sofware, make sure you have properly modified the "/etc/modules" file by adding "w1-gpio" and "w1-therm" and have then rebooted your RPi (IT'S EXTREMELY IMPORTANT). The sofware will tell you anyway if you haven't.

I am still working on this project, there is alot to do to improve it (installer, documentation, code concatenation...) I am only a student so I am still improving, any help or advice will be glady acceted as well as feedback :)

Feel free to use this program wherever and whenever you desire and modify it as much as you like :D




