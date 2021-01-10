import json
from types import SimpleNamespace
import datetime

data = {
    "_index": "dovecot-logs-node1-2020.10.16",
    "_type": "_doc",
    "_id": "c6cPNnUBNRTTExs_ecOX",
    "_score": "null",
    "_source": {
        "geoip": {
            "city_name": "Argelato",
            "country_name": "Italy"
        },
        "@timestamp": "2020-10-16T12:50:35.000Z",
        "host": {
            "hostname": "cp2.utixo.eu"
        },
        "source.ip": "80.104.178.150",
        "source.user.email": "info@ennetipc.it"
    },
    "sort": [
        1602852635000
    ]
}
import time


date = (datetime.datetime.now() - datetime.timedelta(hours=1)).replace(microsecond=0).isoformat()
date += ".000Z"
print(date)