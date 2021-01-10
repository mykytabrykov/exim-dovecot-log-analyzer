ALERTS_INDEX = "alerts-dovecot-new"

class Alert:
    def __init__(self, alert_type, event, user, es_client):
        self.alert_type = alert_type
        self.event = event
        self.user = user
        self.es_client = es_client

    def generate_alert(self):
        if self.alert_type == "dovecot-login-from-another-country":
            #logging.warning("WARNING")
            alert_body = {
                "@timestamp": self.event.document.timestamp,
                "user.email": self.user.document._source.email,
                "user.country.new": self.event.document._source.geoip.country_name,
                #"user.city.new": log.source.location.city,
                "user.ip.new": self.event.document._source.source.ip,
                "host.hostname": self.event.document._source.host.hostname,
                "event.reason": "User has logged in from another country",
                "event.kind": "alert",
                "event.category": "email",
                "event.type": "login_from_new_country",
                "event.outcome": "success"
            }
            # indexing new alert
            self.es_client.index(index=ALERTS_INDEX, body=alert_body)