import json
from types import SimpleNamespace

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

# Parse JSON into an object with attributes corresponding to dict keys.
#x = json.loads(json.dumps(data), object_hook=lambda d: SimpleNamespace(**d))
#print(x)

# x._source.geoip.citq = "lmao"

new_user = object
new_user.document._index = "test"
new_user.document._id = 123
new_user.document._type = "_doc"
#
rex = json.dumps(new_user, default=lambda x: x.__dict__, sort_keys=False, indent=4)
#
# #printable = json.dumps(x.__dict__)
# #print(printable)
#
print(rex)
