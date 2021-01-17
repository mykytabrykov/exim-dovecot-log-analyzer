ALERTS_INDEX = "alerts"


def generate_alert(alert_type, event, user, es_client):
    if alert_type == "dovecot-login-from-another-country":
        # logging.warning("WARNING")
        alert_body = {
            "event.timestamp": event._source.preprocessor.timestamp,
            "user.email": user._source.email,
            "user.country.new": event._source.geoip.country_name,
            # "user.city.new": log.source.location.city,
            "user.ip.new": event._source.source.ip,
            "host.hostname": event._source.host.hostname,
            "event.reason": "User has logged in from another country",
            "event.kind": "alert",
            "event.category": "email",
            "event.type": "login_from_new_country",
            "event.outcome": "success"
        }
        # indexing new alert
        es_client.index(index=ALERTS_INDEX, body=alert_body)