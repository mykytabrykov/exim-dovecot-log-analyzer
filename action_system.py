import os
import configparser
from es_client import EsClient


class ActionSystem:
    def __init__(self, ):
        self.__config = configparser.ConfigParser()
        self.__config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
        self.__es_client = EsClient().connect()

    def generate_alert(self, alert_type, user, options):
        alert_body = {}
        if alert_type == "dovecot-new-region":
            # logging.warning("WARNING")
            alert_body = {
                # "event.timestamp": event._source.preprocessor.timestamp,
                "user.email": user.profile.email,
                "user.country.new": options.key,
                # "user.ip.new": event._source.source.ip,
                "host.hostname": user.profile.hostname,
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
                "user.email": user.profile.email,
                "exim.email.quantity": options,
                # "user.ip.new": event._source.source.ip,
                "host.hostname": user.profile.hostname,
                "event.kind": "alert",
                "event.category": "email",
                "event.type": "sending",
                "event.outcome": "success",
                "event.reason": "User sends too much e-mails...",
            }
            # indexing new alert
        self.__es_client.index(index=self.__config['alerts']['index'], body=alert_body)
