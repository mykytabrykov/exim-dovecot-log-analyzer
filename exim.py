from es_query_template import EsQueryTemplate
from event_manager import EventManager
from user_manager import UserManager
from elasticsearch import Elasticsearch
import serializer
import alert

EXIM_LOGS_INDEX = "exim*"


class Exim:
    def __init__(self, es_config: Elasticsearch, event_manager: EventManager, user_manager: UserManager):
        self.es_config = es_config
        self.event_manager = event_manager
        self.user_manager = user_manager

    def login_failed(self):
        events = self.event_manager.get_events(EsQueryTemplate.exim_login_failed, EXIM_LOGS_INDEX)

        for event in events:
            user = self.user_manager.get_user(event)
            same_ip = False
            for location in user._source.exim.login.failure.locations:
                if location.ip == event._source.source.ip:
                    same_ip = True
                    location.counter += 1
                    break
            if not same_ip:
                try:
                    user._source.exim.login.failure.locations.append(serializer.to_simple_namespace(
                        {
                            "ip": event._source.source.ip,
                            "country": event._source.geoip.country_name,
                            "counter": 1,
                            "last_occurrence": event._source.event.timestamp

                        })
                    )
                except AttributeError:
                    print("Dovecot | Login Failed Error: event: ", event)
                    user._source.exim.login.failure.locations.append(serializer.to_simple_namespace(
                        {
                            "ip": event._source.source.ip,
                            "country": "null",
                            "counter": 1,
                            "last_occurrence": event._source.event.timestamp

                        })
                    )

    def received(self):
        templ = EsQueryTemplate()
        events = self.event_manager.get_events(templ.exim_new_email_received, EXIM_LOGS_INDEX)
        for event in events:
            new_event_manager = EventManager(self.es_config, 100)
            events_by_id = new_event_manager.get_events(templ.exim_event_by_id(event._source.event.id), event._index)
            print("Event id: ", event._source.event.id)
            for event_id in events_by_id:

                print("")
                print(event_id)
            print("====End=====")