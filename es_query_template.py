class EsQueryTemplate:
    dovecot_login_success = {
            "_source": ["@timestamp", "source.ip", "source.user.email", "geoip.country_name", "host.hostname",
                        "geoip.city_name"],
            "sort": [
                {"@timestamp": {"order": "asc"}}
            ],
            "query": {
                "bool": {
                    "filter": {
                        "term": {"pyAnalyzed": "false"}
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