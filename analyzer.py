from es_client import EsClient
from dovecot import Dovecot
from exim import Exim
from user_manager import UserManager
from event_manager import EventManager
from elasticsearch_dsl import connections


class LogAnalyzer:
    def __init__(self):
        # self.es_client = EsConfig().connect()
        # connections.add_connection(conn=self.es_client, alias="default")
        self.dovecot = Dovecot()
        self.exim = Exim()

    def dovecot_scan(self):
        event_max_response_size = 100
        dovecot_index = "dovecot*"

        self.dovecot.suspicious_login()
        self.dovecot.brute_force()
        # event_manager.update_and_flush()  # update python.analyzed field on every used event and remove it from list
        # dovecot.login_failed()  # dovecot successful login analyse
        # event_manager.update_and_flush()
        # user_manager.dump()  # save users to elasticsearch

    def exim_scan(self):
        self.exim.sending_rate()

if __name__ == '__main__':
    log_analyzer = LogAnalyzer()
    log_analyzer.dovecot_scan()