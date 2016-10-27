
from setuptools import setup, find_packages

setup(
    name='OpenDS18B20',
    version='0.9',
    description='DS18B20 auto-detector,reader and mailer for RPi',
    author='jeremy venin',
    author_email='jeremy.venin@telecom-sudparis.eu',
    url='https://github.com/lecreateurfrench/openDS18B20.git',
    #license="",
    packages=['open_ds18b20'],
    entry_points={
        "console_scripts": ['open_ds18b20 = open_ds18b20.__main__:main']
    }
)