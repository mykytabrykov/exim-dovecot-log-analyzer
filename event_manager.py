import serializer
import configparser
import os
from es_client import EsClient
from elasticsearch_dsl import Search, connections, UpdateByQuery

class EventManager:
    def __init__(self, service):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(os.path.dirname(__file__), 'config', 'config.ini'))
        # create default elasticsearch dsl connection
        connections.add_connection(conn=EsClient().connect(), alias="event_manager")
        self.service = service

    def get_events(self, outcome):
        if self.service == 'dovecot':
            if outcome == 'login-successful':
                s = Search(index=self.config['dovecot']['index'], using='event_manager') \
                    .exclude("terms", source__ip=["127.0.0.1", "::1"]) \
                    .filter('term', python__analyzed__keyword='false') \
                    .filter('term', event__action__keyword='login') \
                    .filter('term', event__outcome__keyword='success') \
                    .query("exists", field="geoip.country_name")

                s.aggs.bucket('emails', 'terms', field='source.user.email.keyword', size=1000) \
                    .bucket('by_region', 'terms', field="geoip.country_name.keyword")
                s = s[0:0]
                print(s.to_dict())
                resp = s.execute()
                return resp
            if outcome == 'login-failed':
                s = Search(index=self.config['dovecot']['index'], using='event_manager') \
                    .exclude("terms", source__ip=["127.0.0.1", "::1"]) \
                    .filter('term', python__analyzed__keyword='false') \
                    .filter('term', event__action__keyword='login') \
                    .filter('term', event__outcome__keyword='failure') \
                    .query("exists", field="geoip.country_name")

                s.aggs.bucket('emails', 'terms', field='source.user.email.keyword', size=1000) \
                    .bucket('by_region', 'terms', field="geoip.country_name.keyword")
                s = s[0:0]
                print(s.to_dict())
                resp = s.execute()
                return resp

        elif self.service == 'exim':
            if outcome == 'received':
                s = Search(index="exim*") \
                    .exclude("terms", source__ip=["127.0.0.1", "::1"]) \
                    .filter('term', python__analyzed__keyword='false') \
                    .query("exists", field="event.id")

                s.aggs.bucket('email', 'terms', field='source.user.email.keyword') \
                    .bucket('emails_per_day', 'date_histogram', field="event.timestamp", calendar_interval='day') \
                    .bucket('emails_per_hour', 'date_histogram', field="event.timestamp", calendar_interval='hour') \
                    .bucket('event_id', 'terms', field='event.id.keyword')


    def update_events(self, events, outcome):
        if self.service == 'dovecot':
            if outcome == 'login-successful':
                for email in events.aggregations.emails.buckets:
                    ubq = UpdateByQuery(using='event_manager', index=self.config['dovecot']['index'])\
                        .script(source="ctx._source.python.analyzed = true") \
                        .exclude("terms", source__ip=["127.0.0.1", "::1"]) \
                        .filter('term', python__analyzed__keyword='false') \
                        .filter('term', event__action__keyword='login') \
                        .filter('term', event__outcome__keyword='success') \
                        .filter('term', source__user__email__keyword=email.key) \
                        .query("exists", field="geoip.country_name")
                    print(ubq.to_dict())
                    resp = ubq.execute()
                    print(resp)
            elif outcome == 'login-failed':
                for email in events.aggregations.emails.buckets:
                    ubq = UpdateByQuery(using='event_manager', index=self.config['dovecot']['index'])\
                        .script(source="ctx._source.python.analyzed = true") \
                        .exclude("terms", source__ip=["127.0.0.1", "::1"]) \
                        .filter('term', python__analyzed__keyword='false') \
                        .filter('term', event__action__keyword='login') \
                        .filter('term', event__outcome__keyword='failure') \
                        .filter('term', source__user__email__keyword=email.key) \
                        .query("exists", field="geoip.country_name")
                    print(ubq.to_dict())
                    resp = ubq.execute()
                    print(resp)

    def __flush(self):
        self.events.clear()