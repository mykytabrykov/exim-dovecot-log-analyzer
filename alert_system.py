import os
import configparser
from es_client import EsClient

ALERTS_INDEX = "alerts"

class AlertSystem:
    def __init__(self,):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(os.path.dirname(__file__), 'config', 'config.ini'))
        self.es_client = EsClient().connect()


    def generate_alert(self, service, alert_type, user, options ):
        if service == "dovecot":
            if alert_type == "new-region":
                # logging.warning("WARNING")
                alert_body = {
                    #"event.timestamp": event._source.preprocessor.timestamp,
                    "user.email": user.email,
                    "user.country.new": options.key,
                    #"user.ip.new": event._source.source.ip,
                    "host.hostname": user.hostname,
                    "event.reason": "User has logged in from another country",
                    "event.kind": "alert",
                    "event.category": "email",
                    "event.type": "login_from_new_country",
                    "event.outcome": "success"
                }
                # indexing new alert
                self.es_client.index(index=ALERTS_INDEX, body=alert_body)