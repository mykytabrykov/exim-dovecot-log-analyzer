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

from es_client import EsClient

es_client = EsClient().connect()


s = Search(index='dovecot*') \
    .exclude("terms", source__ip=["127.0.0.1", "::1"]) \
    .filter('term', python__analyzed__keyword='false') \
    .filter('term', event__action__keyword='login') \
    .filter('term', event__outcome__keyword='success') \
    .query("exists", field="geoip.country_name")

s.aggs.bucket('email', 'terms', field='source.user.email.keyword', size=1000) \
        .bucket('by_region', 'terms', field="geoip.country_name.keyword")

s = s[0:0]


print("Query preview: ", s.to_dict())

all_events = s.execute()

for hit in all_events.aggregations.email.buckets:
    print(hit.key)
