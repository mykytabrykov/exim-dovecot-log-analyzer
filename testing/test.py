import json
from types import SimpleNamespace
import datetime
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, A, connections
from elasticsearch_dsl import connections
from es_query_template import EsQueryTemplate

from es_config import EsConfig
query = {
        "query": {
            "bool": {
                "must_not": [
                    {"match": {"source.ip": "127.0.0.1"}},
                    {"match": {"source.ip": "::1"}}
                ],
                "must": [
                    {"match": {"event.action": "login"}},
                    {"match": {"event.outcome": "success"}}
                ]
            }
        }
    }


es_client = EsConfig().get_es_client()

connections.add_connection(conn=es_client, alias="default")

s = Search(index="exim*").filter("term", python__analyzed="false").exclude("terms", source__ip=["127.0.0.1","::1"]).query("exists", field="event.id")


a = A('terms', )
s.aggs.bucket('emails_per_day', 'date_histogram', field="event.timestamp", calendar_interval='day')\
    .bucket('emails_per_hour', 'date_histogram', field="event.timestamp", calendar_interval='hour')\
    .bucket('event_id_terms', "terms", field='event.id.keyword')

print("Query preview: ", s.to_dict())

resp = s.execute()

for event_id_bucket in resp.aggregations.event_id_terms.buckets:
    s1 = Search(using=es_client).index("exim*").filter("term", event__id__keyword=event_id_bucket.key)
    a1 = A('terms', field="event.action.keyword", size=5)
    s1.aggs.bucket('event_action_terms', a1)
    resp = s1.execute()
    #print("s1:", s1.to_dict())

    sent = False
    failed = False
    deferred = False
    sent_event_count = 0
    for event_action_bucket in resp.aggregations.event_action_terms.buckets:
        if event_action_bucket.key == 'email-sent':
            sent = True
            sent_event_count = event_action_bucket.doc_count
        elif event_action_bucket.key == 'email-deferred':
            deferred = True
            deferred_event_count = event_action_bucket.doc_count
        elif event_action_bucket.key == 'email-failed':
            failed = True
            failed_event_count = event_action_bucket.doc_count



    print("Event ID: ", event_id_bucket.key,"Sent:", sent,"(",sent_event_count,")", " - Failed: ", failed, " - Deferred: ", deferred)


#for event_id_bucket in resp:
    #print("event.id", event_id_bucket)


