import os
import configparser
from es_client import EsClient

ALERTS_INDEX = "alerts"


class ActionSystem:
    def __init__(self, ):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(os.path.dirname(__file__), 'config', 'config.ini'))
        self.es_client = EsClient().connect()

    def generate_alert(self, alert_type, user, options):
        alert_body = {}
        if alert_type == "dovecot-new-region":
            # logging.warning("WARNING")
            alert_body = {
                # "event.timestamp": event._source.preprocessor.timestamp,
                "user.email": user.email,
                "user.country.new": options.key,
                # "user.ip.new": event._source.source.ip,
                "host.hostname": user.hostname,
                "event.reason": "Utente si è collegato da un altro paese",
                "event.kind": "alert",
                "event.category": "email",
                "event.type": "login_from_new_country",
                "event.outcome": "success"
            }
            # indexing new alert
        elif alert_type == "exim-sending-rate":
            # logging.warning("WARNING")
            alert_body = {
                # "event.timestamp": event._source.preprocessor.timestamp,
                "user.email": user.email,
                "exim.email.quantity": options,
                # "user.ip.new": event._source.source.ip,
                "host.hostname": user.hostname,
                "event.kind": "alert",
                "event.category": "email",
                "event.type": "sending",
                "event.outcome": "success",
                "event.reason": "Utente spedisce più e-mail del solito",
            }
            # indexing new alert
        self.es_client.index(index=ALERTS_INDEX, body=alert_body)
