import configparser
import os

config = configparser.ConfigParser()

config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

print(config.sections())
print(config['dovecot']['index'])

es_config = config['elasticsearch']

print(es_config.getboolean('ssl'))