from dovecot import Dovecot
from exim import Exim
import os, configparser, logging

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

log_file = os.path.join(os.path.dirname(__file__), config['logging']['log_file_path'])

if os.path.isfile(log_file):
    logging.basicConfig(filename=log_file, level=logging.DEBUG, filemode='a', datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s - %(name)s - %(levelname)-8s: %(message)s')
else:
    f = open(log_file, "x")
    f.write("Log file has been initialized...\n")
    f.close()
    logging.basicConfig(filename=log_file, level=logging.WARNING, filemode='a', datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s - %(name)s - %(levelname)-8s: %(message)s')


class ApiController:
    def __init__(self):
        self.dovecot = Dovecot()
        self.exim = Exim()

    def dovecot_scan(self):
        #self.dovecot.suspicious_login()
        self.dovecot.brute_force()

    def exim_scan(self):
        self.exim.sending_rate()
        # self.exim.brute_force()


if __name__ == '__main__':
    log_analyzer = ApiController()
    log_analyzer.dovecot_scan()
    #log_analyzer.exim_scan()
