from es_client import EsClient
from dovecot import Dovecot
from exim import Exim
from user_manager import UserManager
from elasticsearch_dsl import connections


class ApiController:
    def __init__(self):
        self.dovecot = Dovecot()
        self.exim = Exim()

    def dovecot_scan(self):
        self.dovecot.suspicious_login()
        self.dovecot.brute_force()

    def exim_scan(self):
        self.exim.sending_rate()
        #self.exim.brute_force()


if __name__ == '__main__':
    log_analyzer = ApiController()
    #log_analyzer.dovecot_scan()
    log_analyzer.exim_scan()
