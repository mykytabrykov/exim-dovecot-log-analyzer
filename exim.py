from user import User
from score_system import ScoreSystem
from es_client import EsClient
import statistics
import configparser
import os

from elasticsearch_dsl import Search, UpdateByQuery
from elasticsearch_dsl import connections

EXIM_LOGS_INDEX = "exim*"


class Exim:
    def __init__(self):
        self.score_system = ScoreSystem()

        self.__config = configparser.ConfigParser()
        self.__config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
        self.__config = self.__config['exim']

        connections.add_connection(conn=EsClient().connect(), alias="exim")

    def sending_rate(self):
        #select
        query = Search(using='exim', index=self.__config['index']) \
            .exclude("terms", source__ip=["127.0.0.1", "::1"]) \
            .filter('term', python__analyzed__keyword='false') \
            .query("exists", field="exim.auth")
        #group by
        query.aggs.bucket('emails', 'terms', field='source.user.email.keyword',  size=1000) \
            .bucket('per_day', 'date_histogram', field="event.timestamp", calendar_interval='day')
        # resize
        query = query[0:0]
        # exec
        events = query.execute()

        for email in events.aggregations.emails.buckets:
            user = User(email.key).get_user()
            if user is None:
                user = User(email.key).create_empty_user()
            for day in email.per_day.buckets:
                print(user.profile.to_dict())
                if len(user.profile.exim.emails.sent.daily) > int(self.__config['learning_days']):
                    self.score_system.evaluate_risk('exim-sending-rate', user, day.doc_count)
                user.profile.exim.emails.sent.daily.append(day.doc_count)
            user.update()

        for email in events.aggregations.emails.buckets:
            ubq = UpdateByQuery(using='exim', index=self.__config['index']) \
                .script(source="ctx._source.python.analyzed = true") \
                .exclude("terms", source__ip=["127.0.0.1", "::1"]) \
                .filter('term', python__analyzed__keyword='false') \
                .filter('term', event__action__keyword='login') \
                .filter('term', event__outcome__keyword='failure') \
                .filter('term', source__user__email__keyword=email.key) \
                .query("exists", field="geoip.country_name")
            ubq.execute()

    def brute_force(self):
        query = Search(using='exim', index=self.__config['index']) \
            .exclude("terms", source__ip=["127.0.0.1", "::1"]) \
            .filter('term', python__analyzed__keyword='false') \
            .filter('term', event__action__keyword='login') \
            .filter('term', event__outcome__keyword='failure') \
            .query("exists", field="geoip.country_name")

        query.aggs.bucket('emails', 'terms', field='source.user.email.keyword', size=1000) \
            .bucket('by_region', 'terms', field="geoip.country_name.keyword")
        query = query[0:0]


        events = query.execute()

        for email in events.aggregations.emails.buckets:
            user = user = User(email.key).get_user()
            if user is not None:
                for region in email.by_region.buckets:
                    self.score_system.evaluate_risk('exim-login-failed', user, region)
                user.update()

        for email in events.aggregations.emails.buckets:
            ubq = UpdateByQuery(using='exim', index=self.__config['index']) \
                .script(source="ctx._source.python.analyzed = true") \
                .exclude("terms", source__ip=["127.0.0.1", "::1"]) \
                .filter('term', python__analyzed__keyword='false') \
                .filter('term', event__action__keyword='login') \
                .filter('term', event__outcome__keyword='failure') \
                .filter('term', source__user__email__keyword=email.key) \
                .query("exists", field="geoip.country_name")
            # print(ubq.to_dict())
            ubq.execute()
