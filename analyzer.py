from es_config import EsConfig
from dovecot import Dovecot
from user_manager import UserManager
from event_manager import EventManager


class LogAnalyzer:
    def __init__(self):
        self.es_client = EsConfig().get_es_client()

    def dovecot(self):
        event_max_response_size = 10
        dovecot_index = "dovecot*"

        user_manager = UserManager(self.es_client)
        event_manager = EventManager(self.es_client, dovecot_index, event_max_response_size)
        dovecot = Dovecot(self.es_client, user_manager, event_manager)
        dovecot.login_successful()  # dovecot successful login analyse
        user_manager.dump()  # save users to elasticsearch
        event_manager.update()  # update pyAnalyzed field on every used event


if __name__ == '__main__':
    log_analyzer = LogAnalyzer()
    log_analyzer.dovecot()