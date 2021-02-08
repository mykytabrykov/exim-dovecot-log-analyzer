from es_query_template import EsQueryTemplate
from event_manager import EventManager
from user_manager import UserManager
from score_system import ScoreSystem
from elasticsearch import Elasticsearch
import serializer
from es_client import EsClient
import alert_system

from elasticsearch_dsl import Search, A, connections, Document
from elasticsearch_dsl import connections

EXIM_LOGS_INDEX = "exim*"


class Exim:
    def __init__(self):
        self.event_manager = EventManager("exim")
        self.user_manager = UserManager("exim")
        self.score_system = ScoreSystem("exim")


    def sending_rate(self):
        s = Search(index="exim*") \
            .exclude("terms", source__ip=["127.0.0.1", "::1"]) \
            .filter('term', python__analyzed__keyword='false') \
            .query("exists", field="event.id")

        s.aggs.bucket('email', 'terms', field='source.user.email.keyword') \
            .bucket('emails_per_day', 'date_histogram', field="event.timestamp", calendar_interval='day') \
            .bucket('emails_per_hour', 'date_histogram', field="event.timestamp", calendar_interval='hour') \
            .bucket('event_id', 'terms', field='event.id.keyword')


        print(s.to_dict())

        # response = s.execute()
        #
        # for email in response.aggregations.email.buckets:
        #     daily_received_emails = []
        #     hourly_received_emails = []

    def login_failed(self):
        events = self.event_manager.get_events(EsQueryTemplate.exim_login_failed, EXIM_LOGS_INDEX)

        for event in events:
            user = self.user_manager.get_user(event)
            same_ip = False
            for location in user._source.exim_scan.login.failure.locations:
                if location.ip == event._source.source.ip:
                    same_ip = True
                    location.counter += 1
                    break
            if not same_ip:
                try:
                    user._source.exim_scan.login.failure.locations.append(serializer.to_simple_namespace(
                        {
                            "ip": event._source.source.ip,
                            "country": event._source.geoip.country_name,
                            "counter": 1,
                            "last_occurrence": event._source.preprocessor.timestamp

                        })
                    )
                except AttributeError:
                    print("Dovecot | Login Failed Error: event: ", event)
                    user._source.exim_scan.login.failure.locations.append(serializer.to_simple_namespace(
                        {
                            "ip": event._source.source.ip,
                            "country": "null",
                            "counter": 1,
                            "last_occurrence": event._source.preprocessor.timestamp

                        })
                    )

