from es_query_template import EsQueryTemplate
from logManager import LogManager
DOVECOT_LOGS_INDEX = "dovecot*"

class Dovecot:
    def __init__(self):
        self.es_query_template = EsQueryTemplate
        self.log_manager = LogManager()

    def login_successful(self, es_client):
        logs = self.log_manager.get_logs(es_client, self.es_query_template.dovecot_login_success, DOVECOT_LOGS_INDEX)
        for log in logs:
            print (log)