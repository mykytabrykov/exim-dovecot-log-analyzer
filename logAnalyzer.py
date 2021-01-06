from document import Document
import logging
from es_config import EsConfig
import uuid

'''
"_source" : {
  "email" : "mykytabrykov@gmail.com ",
  "hostname" : "cp7",
  "logins" : {
    "success" : {
      "locations" : [
        {
          "ip" : "123.123.123.123",
          "country" : "Italy",
          "times" : 5
        },
        {
          "ip" : "322.22.21.11",
          "description" : "Germany",
          "times" : 2
        }
      ]
    }
  }
}
'''

# log_file = "/var/utixo/logs/country.log"
log_file = "logs/country.log"

logging.basicConfig(filename=log_file, level=logging.INFO, filemode='a', datefmt='%Y-%m-%d %H:%M:%S',
                    format='%(asctime)s - %(name)s - %(levelname)-8s: %(message)s')

DOVECOT_LOGS_INDEX = "dovecot*"
DOVECOT_USERS_INDEX = "users-dovecot-new"
DOVECOT_ALERTS_INDEX = "alerts-dovecot-new"
RESPONSE_SIZE = "10000"

class LogAnalyzer:
    def __init__(self):
        self.es = EsConfig().get_es()
        self.users = []  # list of users' documents created at runtime of this program

    def __get_user(self, log):
        for user_doc in self.users:
            if user_doc.user.email == log.event.email and user_doc.user.hostname == log.event.hostname:
                # print("User already exist inside runtime users' list. Return his document to caller...")
                return user_doc
        # user does not exist at runtime, need to be retrieved from es
        query = {
            "query": {
                "bool": {
                    "filter": {
                        "term": {"email.keyword": log.event.email}
                    }
                }
            }
        }
        res = self.es.search(index=DOVECOT_USERS_INDEX, body=query)
        if res['hits']['total']['value'] != 0:  # user exist inside the index -> append and return it to caller method
            user_doc = Document(user=res['hits']['hits'][0])
            self.users.append(user_doc)  # append new user's document
            return user_doc
        else:  # user does not exist, need to be created...
            new_user_json = {
                "_type": "_doc",
                "_index": DOVECOT_USERS_INDEX,
                "_id": uuid.uuid4().__str__(),
                "_source": log.user_json_representation()
            }
            # print(new_user_json)
            user_doc = Document(user=new_user_json)
            self.users.append(user_doc)
            return user_doc

    def __get_logs(self):
        logs = []
        query = {
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

        res = self.es.search(index=DOVECOT_LOGS_INDEX, body=query, size=RESPONSE_SIZE)

        if res['hits']['total']['value'] != 0:  # if there are some not analyzed docs
            event_list = res['hits']['hits'].copy()
            for i in range(len(event_list)):
                logs.append(Document(event=event_list[i]))
                # print("Log num.", i, event_list[i])
        return logs

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
        self.es.index(index=DOVECOT_ALERTS_INDEX, body=body)
        # updating user's data with new country

    # except Exception as error:
    #     print("Error1: ", error)
    #     print(login_list[i])

    def update_users(self):
        for user_doc in self.users:
            body = {
                "doc": user_doc.user.to_json(),
                'doc_as_upsert': "true"
            }
            res = self.es.update(index=user_doc.index, id=user_doc.id, body=body)
        # print("Update_users result: ", end="")
        # print(res)

    def control_country(self):
        logs = self.__get_logs()
        for log in logs:
            user = self.__get_user(log)
            # print("User: ", user)
            if not user.user.check_country(log.event.location):
                print("Raise alert...")
                self.__generate_alert(log, user)
            self.es.update(index=log.index, id=log.id, body={"doc": {"pyAnalyzed": "true"}})
        self.update_users()
