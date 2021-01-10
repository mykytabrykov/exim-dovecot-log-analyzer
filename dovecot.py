from es_query_template import EsQueryTemplate
from event_manager import EventManager
from user_manager import UserManager
from elasticsearch import Elasticsearch
from types import SimpleNamespace
from alert import Alert

DOVECOT_LOGS_INDEX = "dovecot*"


class Dovecot:
    def __init__(self, es_client: Elasticsearch, user_manager: UserManager, event_manager: EventManager):
        self.es_client = es_client
        self.event_manager = event_manager
        self.user_manager = user_manager

    def login_successful(self):
        events = self.event_manager.get_events(EsQueryTemplate.dovecot_login_success,
                                               DOVECOT_LOGS_INDEX)
        for event in events:
            user = self.user_manager.get_user(event)
            same_ip = False
            same_country = False
            for location in user._source.login.success.locations:
                try:
                    if location.ip == event._source.source.ip:
                        same_ip = True
                    if location.country == event._source.geoip.country_name:
                        same_country = True
                    if location.ip == event._source.source.ip and location.country == event._source.geoip.country_name:
                        location.counter += 1
                        break
                except AttributeError:
                    print("An AttributeError has occured | location data is: ", location)
            if not same_ip:
                user._source.login.success.locations.append(
                    SimpleNamespace(country=event._source.geoip.country_name,
                                    ip=event._source.source.ip, counter=1))
                if not same_country:
                    alert = Alert("dovecot-login-from-another-country", event, user, self.es_client)
                    alert.generate_alert()

    def login_failed(self):
        events = self.event_manager.get_events(EsQueryTemplate.dovecot_login_failed,
                                               DOVECOT_LOGS_INDEX)
        for event in events:
            user = self.user_manager.get_user(event)