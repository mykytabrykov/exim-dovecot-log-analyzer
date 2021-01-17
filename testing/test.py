import json
from types import SimpleNamespace
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, A, connections, Document, Q, Date
from elasticsearch_dsl import connections
import statistics
import serializer
import time
from es_query_template import EsQueryTemplate

from es_config import EsConfig


es_client = EsConfig().get_es_client()

connections.add_connection(conn=es_client, alias="default")

all_events_search= Search(index="exim*") \
    .exclude("terms", source__ip=["127.0.0.1", "::1"])\
    .filter('term', python__analyzed__keyword='false')\
    .query("exists", field="event.id")

all_events_aggr_search = all_events_search.filter('term', event__action__keyword='received')
all_events_aggr_search.aggs.bucket('user_email_bucket', 'terms', field='source.user.email.keyword')\
                            .bucket('emails_per_day', 'date_histogram', field="event.timestamp", calendar_interval='day')\
                            .bucket('emails_per_hour', 'date_histogram', field="event.timestamp", calendar_interval='hour')\
                            .bucket('event_id', 'terms', field='event.id.keyword')\


#all_events_aggr_search.aggs.bucket('event_id_bucket', 'terms', field='event.id.keyword', size=5000)\
                            #.bucket('event_action_bucket', 'terms', field='event.action.keyword')


# all_events_search.aggs.bucket('all_events_bucket', 'terms', field='event.id.keyword')\
#                     .bucket('action_bucket', 'terms', field='event.action.keyword')

#all_events_search = all_events_search[0:1]
print("Query preview: ", all_events_search.to_dict())

all_events = all_events_aggr_search.execute()
for email_bucket in all_events.aggregations.user_email_bucket.buckets:
    #print('Email', email_bucket.key, " - Total new email send", email_bucket.doc_count)
    daily_delivered_emails = []
    daily_failed_emails = []
    hourly_delivered_emails = []
    hourly_failed_emails = []
    print("====================")
    print("Email: ", email_bucket.key)
    for day_bucket in email_bucket.emails_per_day.buckets:
        #day = datetime.strptime(day_bucket.key_as_string, "%Y-%m-%dT%H:%M:%S.%fZ")
        #print(day, " : ", day_bucket.doc_count)
        #daily_delivered_emails.append(day_bucket.doc_count)
        delivered_email_per_day_count = 0
        failed_email_per_day_count = 0
        for hour_bucket in day_bucket.emails_per_hour.buckets:
            #hourly_delivered_emails.append(hour_bucket.doc_count)
            #print(hour_bucket.key_as_string)
            delivered_email_per_hour_count = 0
            failed_email_per_hour_count = 0
            for event_id in hour_bucket.event_id.buckets:
                event_by_id_search = all_events_search.filter('term', event__id__keyword=event_id.key)\
                                                        .exclude('term', event__action__keyword='received')
                event_by_id_search.aggs.bucket('action', 'terms', field='event.action.keyword')
                print("Q2 preview: ", event_by_id_search.to_dict())
                response = event_by_id_search.execute()
                for event_by_id in response.aggregations.action.buckets:
                    if event_by_id.key == 'delivered':
                        delivered_email_per_day_count += event_by_id.doc_count
                        delivered_email_per_hour_count += event_by_id.doc_count
                    if event_by_id.key == 'failed':
                        failed_email_per_day_count += event_by_id.doc_count
                        failed_email_per_hour_count += event_by_id.doc_count
            hourly_delivered_emails.append(delivered_email_per_hour_count)
            hourly_failed_emails.append(failed_email_per_hour_count)
        daily_delivered_emails.append(delivered_email_per_day_count)
        daily_failed_emails.append(failed_email_per_day_count)
    print("Hourly Variance:", statistics.pvariance(hourly_delivered_emails))
    print("Hourly Deviation:", statistics.pstdev(hourly_delivered_emails))
    print("Hourly Mean: ", statistics.mean(hourly_delivered_emails))
    print("Hour RSD: ", statistics.pstdev(hourly_delivered_emails) / statistics.mean(hourly_delivered_emails))

    print("Daily Variance:", statistics.variance(daily_delivered_emails))
    print("Daily Deviation:", statistics.stdev(daily_delivered_emails))
    print("Daily Mean: ", statistics.mean(daily_delivered_emails))
    print("Day RSD: ", statistics.stdev(daily_delivered_emails) / statistics.mean(daily_delivered_emails))






# s.aggs.bucket('event_id_terms', "terms", field='event.id.keyword')\
#     .bucket('emails_per_day', 'date_histogram', field="event.timestamp", calendar_interval='day')\
#     .bucket('emails_per_hour', 'date_histogram', field="event.timestamp", calendar_interval='hour') \
#     .bucket('event_action_terms', 'terms', field='event.action.keyword')
# print("Going to sleep for 10 seconds...")
# time.sleep(10)
# print(dir(all_events))



        #print("bucket", event, "id: ", received.event.id)
    #print("test1", received.event.action)



#     #d = Document.get(id=received.meta.id)
#     #print("doc", d)
#     print(event.event.id)

#     s1.aggs.bucket('event_action_bucket', "terms", field='event.action.keyword')
#     print("s1 preview: ", s1.to_dict())
#     resp_by_id = s1.execute()
#
#     for result in resp_by_id.aggregations.event_action_bucket.buckets:
#         #for id in s1.filter("term", event__action__keyword="delivered"):
#         print("test : ", result.event.action)
#
#         delivered = False
#         deferred = False
#         failed = False
#
#         delivered_counter = 0
#         deferred_counter = 0
#         failed_counter = 0
#
#         if result.key == 'delivered':
#             delivered = True
#             delivered_counter = result.doc_count
#             s2 = Search(index="exim*").filter("term", event__id__keywod=event.event.id)
#
#         elif result.key == 'deferred':
#             deferred = True
#             deferred_counter = result.doc_count
#         elif result.key == 'failed':
#             failed = True
#             failed_counter = result.doc_count
#
#
#     print("Event ID: ", event.event.id, "Sent:", delivered, "(", delivered_counter, ")", " - Failed: ", failed,
#           " - Deferred: ", deferred)
#
#
#     # s1 = Search(using=es_client).index("exim*").filter("term", event__id__keyword=received.key)
#     # a1 = A('terms', field="event.action.keyword", size=5)
#     # s1.aggs.bucket('event_action_terms', a1)
#     # response = s1.execute()
#     # #print("s1:", s1.to_dict())
#     #
#
#
#
#
#
#
#
# #for event_id_bucket in resp:
#     #print("event.id", event_id_bucket)
