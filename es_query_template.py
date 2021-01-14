class EsQueryTemplate:
    dovecot_login_success = {
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

    dovecot_login_failed = {
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
                    {"match": {"event.outcome": "failure"}}
                ]
            }
        }
    }

    exim_login_failed = {
        "_source": ["event.timestamp",
                    "source.ip",
                    "source.user.id",
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
                    {"match": {"event.outcome": "failure"}}
                ]
            }
        }
    }

    exim_new_email_received = {
        "_source": ["event.timestamp",
                    "event.id",
                    "exim.auth",
                    "source.ip",
                    "source.user.email",
                    "geoip.country_name",
                    "host.hostname",
                    "event.action",
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
                    {"match": {"event.action.keyword": "new-email-received"}}
                ]
            }
        }
    }

    def exim_event_by_id(self, id):
        query= {
            "_source": ["event.timestamp",
                        "event.id",
                        "exim.auth",
                        "source.ip",
                        "source.user.email",
                        "geoip.country_name",
                        "host.hostname",
                        "event.action",
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
                        {"match": {"event.id.keyword": id}}
                    ]
                }
            }
        }
        return query

    exim_login_failed = {
        "_source": ["event.timestamp",
                    "source.ip",
                    "source.user.id",
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
                    {"match": {"event.outcome": "failure"}}
                ]
            }
        }
    }

    exim_new_email_received = {
        "_source": ["event.timestamp",
                    "event.id",
                    "exim.auth",
                    "source.ip",
                    "source.user.email",
                    "geoip.country_name",
                    "host.hostname",
                    "event.action",
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
                    {"match": {"event.action.keyword": "new-email-received"}}
                ]
            }
        }
    }

    def exim_event_by_id(self, id):
        query= {
            "_source": ["event.timestamp",
                        "event.id",
                        "exim.auth",
                        "source.ip",
                        "source.user.email",
                        "geoip.country_name",
                        "host.hostname",
                        "event.action",
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
                        {"match": {"event.id.keyword": id}}
                    ]
                }
            }
        }
        return query