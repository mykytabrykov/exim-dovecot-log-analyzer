DOVECOT_ALERTS_INDEX = "alerts-dovecot-new"


def __generate_alert(self, log, user):
    logging.warning("WARNING")
    body = {
        "@timestamp": log.event.timestamp,
        "user.email": user.user.email,
        "user.country.new": log.event.location.country,
        "user.city.new": log.event.location.city,
        "user.ip.new": log.event.location.ip,
        "host.hostname": log.event.hostname,
        "event.reason": "User logged in from another country",
        "event.kind": "alert",
        "event.category": "email",
        "event.type": "login_from_new_country",
        "event.outcome": "success"
    }
    # indexing new alert
    self.es_client.index(index=DOVECOT_ALERTS_INDEX, body=body)
    # updating user's data with new country