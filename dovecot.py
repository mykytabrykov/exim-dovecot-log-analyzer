import configparser, logging, os
from score_system import ScoreSystem
from user import User
from elasticsearch_dsl import Search, connections, UpdateByQuery
from es_client import EsClient


class Dovecot:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
        # create default elasticsearch dsl connection for dovecot
        connections.add_connection(conn=EsClient().connect(), alias="dovecot")

        self.score_system = ScoreSystem()

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
            user = User(email.key).get_user()
            if user is None:
                user = User(email.key).create_empty_user()
                for region in email.by_region.buckets:
                    user.profile.dovecot.login.success.locations.append({
                        "region": region.key,
                        "counter": region.doc_count,
                        "new": "no"
                    })
            else:
                for region in email.by_region.buckets:
                    for location in user.profile.dovecot.login.success.locations:
                        if location.region == region.key:
                            location.counter += region.doc_count
                            region.doc_count = 0
                    if region.doc_count != 0:
                        self.score_system.evaluate_risk("dovecot-new-region", user, region)
                        user.profile.dovecot.login.success.locations.append({
                            "region": region.key,
                            "counter": region.doc_count,
                            "new": "yes"
                        })
            user.update()


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
        logging.info('Entering suspicious_login method')
        query = Search(using='dovecot', index=self.config['dovecot']['index']) \
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
            user = User(email.key).get_user()
            if user is not None:
                for region in email.by_region.buckets:
                    print('login-failed-alert')
                    self.score_system.evaluate_risk('dovecot-login-failed', user, region)
            user.update()


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
