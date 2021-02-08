from score_system import ScoreSystem
from user_manager import UserManager
from elasticsearch_dsl import Search, connections, UpdateByQuery
import configparser
import os
from es_client import EsClient


class Dovecot:
    def __init__(self):
        self.user_manager = UserManager()
        self.score_system = ScoreSystem()

        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(os.path.dirname(__file__), 'config', 'config.ini'))
        # create default elasticsearch dsl connection
        connections.add_connection(conn=EsClient().connect(), alias="dovecot")


    def suspicious_login(self):
        # select
        query = Search(using='dovecot', index=self.config['dovecot']['index']) \
            .exclude("terms", source__ip=["127.0.0.1", "::1"]) \
            .filter('term', python__analyzed__keyword='false') \
            .filter('term', event__action__keyword='login') \
            .filter('term', event__outcome__keyword='success') \
            .query("exists", field="geoip.country_name")

        # group by
        query.aggs.bucket('emails', 'terms', field='source.user.email.keyword', size=1000) \
            .bucket('by_region', 'terms', field="geoip.country_name.keyword")
        # we need only the aggregation part
        query = query[0:0]
        print(query.to_dict())
        # execute query
        events = query.execute()

        for email in events.aggregations.emails.buckets:
            user = self.user_manager.get_user(email.key)
            if user is None:
                user = self.user_manager.create_empty_user(email.key)
                for region in email.by_region.buckets:
                    user.dovecot.login.success.locations.append({
                        "region": region.key,
                        "counter": region.doc_count,
                        "alert": "no"
                    })
            else:
                for region in email.by_region.buckets:
                    for location in user.dovecot.login.success.locations:
                        if location.region == region.key:
                            location.counter += region.doc_count
                            region.doc_count = 0
                    if region.doc_count != 0:
                        self.score_system.evaluate_risk("dovecot-new-region", user, region)
                        user.dovecot.login.success.locations.append({
                            "region": region.key,
                            "counter": region.doc_count,
                            "alert": "yes"
                        })

        self.user_manager.update_users()

        # mark events as already checked
        for email in events.aggregations.emails.buckets:
            ubq = UpdateByQuery(using='dovecot', index=self.config['dovecot']['index']) \
                .script(source="ctx._source.python.analyzed = true") \
                .exclude("terms", source__ip=["127.0.0.1", "::1"]) \
                .filter('term', python__analyzed__keyword='false') \
                .filter('term', event__action__keyword='login') \
                .filter('term', event__outcome__keyword='success') \
                .filter('term', source__user__email__keyword=email.key) \
                .query("exists", field="geoip.country_name")
            # print(ubq.to_dict())
            ubq.execute()

    def brute_force(self):
        query = Search(using='dovecot', index=self.config['dovecot']['index'] ) \
            .exclude("terms", source__ip=["127.0.0.1", "::1"]) \
            .filter('term', python__analyzed__keyword='false') \
            .filter('term', event__action__keyword='login') \
            .filter('term', event__outcome__keyword='failure') \
            .query("exists", field="geoip.country_name")

        query.aggs.bucket('emails', 'terms', field='source.user.email.keyword', size=1000) \
            .bucket('by_region', 'terms', field="geoip.country_name.keyword")
        query = query[0:0]
        # print(query.to_dict())
        events = query.execute()

        for email in events.aggregations.emails.buckets:
            user = self.user_manager.get_user(email.key)
            if user is not None:
                for region in email.by_region.buckets:
                    print('login-failed-alert')
                    self.score_system.evaluate_risk('dovecot-login-failed', user, region)

        self.user_manager.update_users()
        for email in events.aggregations.emails.buckets:
            ubq = UpdateByQuery(using='dovecot', index=self.config['dovecot']['index']) \
                .script(source="ctx._source.python.analyzed = true") \
                .exclude("terms", source__ip=["127.0.0.1", "::1"]) \
                .filter('term', python__analyzed__keyword='false') \
                .filter('term', event__action__keyword='login') \
                .filter('term', event__outcome__keyword='failure') \
                .filter('term', source__user__email__keyword=email.key) \
                .query("exists", field="geoip.country_name")
            # print(ubq.to_dict())
            ubq.execute()

