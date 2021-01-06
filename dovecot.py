from es_query_template import EsQueryTemplate
from event_manager import EventManager
from user_manager import UserManager
from elasticsearch import Elasticsearch
DOVECOT_LOGS_INDEX = "dovecot*"


class Dovecot:
    def __init__(self, es_client: Elasticsearch, user_manager: UserManager, event_manager: EventManager):
        self.es_client = es_client
        self.event_manager = event_manager
        self.user_manager = user_manager

    def login_successful(self):
        events = self.event_manager.get_events(self.es_client, EsQueryTemplate.dovecot_login_success, DOVECOT_LOGS_INDEX)
        for event in events:
            #user = self.user_manager.get_user(event.document._source)
            print(event.document._source)