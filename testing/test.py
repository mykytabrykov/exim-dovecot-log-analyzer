import json
from types import SimpleNamespace
import datetime
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, A
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

s = Search(using=es_client).index("exim*").filter("term", python__analyzed="false").exclude("terms", source__ip=["127.0.0.1","::1"]).query("exists", field="event.id")


a = A('terms', field='event.id.keyword', size=25)
s = s[0:15]
s.aggs.bucket('event_id_terms', a)

resp = s.execute()
print("resp: ", dir(resp))
print("Dict: ", s.to_dict())
print("aggs1", s.aggs['event_id_terms'])



for hit in resp.aggregations.event_id_terms.buckets:
    s1 = Search(using=es_client).index("exim*").filter("term", event__id__keyword=hit.key)
    a1 = A('terms', field="event.action.keyword", size=5)
    s1.aggs.bucket('event_action_terms', a1)
    s1 = s1[0:hit.doc_count]
    resp = s1.execute()

    print("s1:", s1.to_dict())
    for hit0 in resp.aggregations.event_action_terms.buckets:
        print(hit0)
    for hit1 in s1:
        print("Ev.id", hit1.event.id, "event.action", hit1.event.action)
    break

for hit in resp:
    print("event.id", hit)


