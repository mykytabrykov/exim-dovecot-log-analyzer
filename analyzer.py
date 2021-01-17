from es_config import EsConfig
from dovecot import Dovecot
from exim import Exim
from user_manager import UserManager
from event_manager import EventManager
from elasticsearch_dsl import connections


class LogAnalyzer:
    def __init__(self):
        self.es_client = EsConfig().get_es_client()
        connections.add_connection(conn=self.es_client, alias="default")

    def dovecot(self):
        event_max_response_size = 100
        dovecot_index = "dovecot*"

        user_manager = UserManager(self.es_client)
        event_manager = EventManager(self.es_client, event_max_response_size)
        dovecot = Dovecot(self.es_client, user_manager, event_manager)
        dovecot.login_successful()
        event_manager.update_and_flush()  # update python.analyzed field on every used event and remove it from list
        dovecot.login_failed()  # dovecot successful login analyse
        event_manager.update_and_flush()
        user_manager.dump()  # save users to elasticsearch

    def exim(self):
        event_max_response_size = 10
        user_manager = UserManager(self.es_client)
        event_manager = EventManager(self.es_client, event_max_response_size)
        exim = Exim(self.es_client, event_manager, user_manager)
        #exim.login_failed()
        #user_manager.dump()
        exim.received()

if __name__ == '__main__':
    log_analyzer = LogAnalyzer()
    log_analyzer.exim()