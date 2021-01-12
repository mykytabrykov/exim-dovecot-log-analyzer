import json
from types import SimpleNamespace
import datetime
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, A

from es_config import EsConfig
query = {
        "_source": ["event.timestamp",
                    "source.ip",
                    "source.user.email",
                    "geoip.country_name",
                    "host.hostname",
                    "geoip.city_name"],
        "sort": [
            {"@timestamp": {"order": "asc"}}
        ],
        "query": {
            "bool": {
                "filter": {
                    "term": {"python.analyzed": "false"}
                },
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

es = EsConfig().get_es_client()

s = Search(using=es, index="exim*")

s.filter("term", python__analyzed="false")

response = s.execute()

for hit in response:
    print(hit.event.timestamp)
