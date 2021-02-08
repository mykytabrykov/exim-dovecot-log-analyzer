from es_query_template import EsQueryTemplate
from event_manager import EventManager
from score_system import ScoreSystem
from user_manager import UserManager
from elasticsearch import Elasticsearch
import serializer
import alert_system


class Dovecot:
    def __init__(self):
        self.event_manager = EventManager("dovecot")
        self.user_manager = UserManager("dovecot")
        self.score_system = ScoreSystem("dovecot")
        # scoresystem

    def suspicious_login(self):
        events = self.event_manager.get_events('login-successful')

        for email in events.aggregations.emails.buckets:
            user = self.user_manager.get_user(email.key)
            if user is None:
                resp = self.user_manager.create_user(email.key)
                if resp['result'] != 'created':
                    raise Exception
                user = self.user_manager.get_user(email.key)
            if len(user.dovecot.login.success.locations) == 0:
                for region in email.by_region.buckets:
                    user.dovecot.login.success.locations.append({
                        "region": region.key,
                        "counter": region.doc_count,
                        "alert": "no"
                    })
            else:
                print('hey')
                for region in email.by_region.buckets:
                    for location in user.dovecot.login.success.locations:
                        if location.region == region.key:
                            print("before:", region.doc_count)
                            location.counter += region.doc_count
                            region.doc_count = 0
                            print("after:", region.doc_count)
                        break
                    if region.doc_count != 0:
                        self.score_system.evaluate_risk("new-region", user, region)
                        user.dovecot.login.success.locations.append({
                            "region": region.key,
                            "counter": region.doc_count,
                            "alert": "yes"
                        })

        self.user_manager.update_users()
        self.event_manager.update_events(events, "login-successful")

    def brute_force(self):
        events = self.event_manager.get_events('login-failed')
        for email in events.aggregations.emails.buckets:
            user = self.user_manager.get_user(email.key)
            if user is not None:
                for region in email.by_region.buckets:
                    print('login-failed-alert')
                    self.score_system.evaluate_risk('login-failed', user, region)

        self.user_manager.update_users()
        self.event_manager.update_events(events, "login-failure")
# events = self.event_manager.get_events(EsQueryTemplate.dovecot_login_failed,
#                                        DOVECOT_LOGS_INDEX)
# for event in events:
#     user = self.user_manager.get_user(event)
#     same_ip = False
#     for location in user._source.login.failure.locations:
#         if location.ip == event._source.source.ip:
#             same_ip = True
#             location.counter += 1
#             break
#     if not same_ip:
#         try:
#             user._source.login.failure.locations.append(serializer.to_simple_namespace(
#                 {
#                     "ip": event._source.source.ip,
#                     "country": event._source.geoip.country_name,
#                     "counter": 1,
#                     "last_occurrence": event._source.preprocessor.timestamp
#
#                 })
#             )
#         except AttributeError:
#             print("Dovecot | Login Failed Error: event: ", event)
#             user._source.login.failure.locations.append(serializer.to_simple_namespace(
#                 {
#                     "ip": event._source.source.ip,
#                     "country": "null",
#                     "counter": 1,
#                     "last_occurrence": event._source.preprocessor.timestamp
#
#                 })
#             )
