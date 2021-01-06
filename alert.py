DOVECOT_ALERTS_INDEX = "alerts-dovecot-new"


def __generate_alert(self, log, user):
    logging.warning("WARNING")
    body = {
        "@timestamp": log.source.timestamp,
        "user.email": user.source.email,
        "user.country.new": log.source.location.country,
        "user.city.new": log.source.location.city,
        "user.ip.new": log.source.location.ip,
        "host.hostname": log.source.hostname,
        "event.reason": "User logged in from another country",
        "event.kind": "alert",
        "event.category": "email",
        "event.type": "login_from_new_country",
        "event.outcome": "success"
    }
    # indexing new alert
    self.es_client.index(index=DOVECOT_ALERTS_INDEX, body=body)
    # updating user's data with new country