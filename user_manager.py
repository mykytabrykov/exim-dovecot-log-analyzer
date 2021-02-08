import serializer
import uuid
import datetime
from elasticsearch_dsl import Search, connections
import configparser
import os
from es_client import EsClient
from pytz import timezone
import time
USERS_INDEX = "users-cpanel"


class UserManager:

    def __init__(self, service):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(os.path.dirname(__file__), 'config', 'config.ini'))
        self.es_client = EsClient().connect()
        connections.add_connection(conn=self.es_client, alias="user_manager")
        self.users = []
        self.service = service

    def get_user(self, email):
        for user in self.users:
            if user.email == email:
                # print("User already exist inside runtime users' list. Return his document to caller...")
                return user
        # user does not exist at runtime, need to be retrieved from elasticsearch
        s = Search(index=self.config['users']['index'], using='user_manager') \
            .filter('term', email__keyword=email)
        #print(s.to_dict())
        response = s.execute()
        for user in response:
            self.users.append(user)
            return user

        return None




    def create_user(self, email):
        s = Search()
        if self.service == 'dovecot':
            s = Search(index=self.config['dovecot']['index'], using='user_manager') \
                .exclude("terms", source__ip=["127.0.0.1", "::1"]) \
                .filter('term', python__analyzed__keyword='false') \
                .filter('term', event__action__keyword='login') \
                .filter('term', event__outcome__keyword='success') \
                .filter('term', source__user__email__keyword=email) \
                .query("exists", field="geoip.country_name") \
                .sort('@timestamp')
            s = s[0:1]

        print(s.to_dict())
        response = s.execute()
        for event in response:
            new_user_json = {
                "_type": "user",
                "_index": self.config['users']['index'],
                "_id": uuid.uuid4().__str__(),
                "_source": {
                    "last_update": datetime.datetime.now(timezone('UTC')).isoformat(),
                    "email": event.source.user.email,
                    "hostname": event.host.name,
                    "score": 0.0001,
                    "dovecot": {
                        "login": {
                            "success": {
                                "locations": []
                            },
                            "failure": {
                                "locations": []
                            }
                        }
                    },
                    "exim": {
                        "emails": {
                            "sent": {
                                "total": 0
                            }
                        },
                        "login": {
                            "failure": {
                                "locations": []
                            }
                        }
                    }
                }
            }
            res = self.es_client.index(index=new_user_json['_index'], id=new_user_json['_id'], body=new_user_json['_source'])
            # time need to ingestion by Elasticsearch
            time.sleep(1)
            return res

    def update_users(self):
        for user in self.users:
            user.last_update = datetime.datetime.now(timezone('UTC')).isoformat()
            user_dict = user.to_dict()
            print(user_dict)
            body = {
                "doc": serializer.to_json(user_dict),
                "doc_as_upsert": "true"
            }
            self.es_client.update(index=user.meta.index, id=user.meta.id, body=body)
            self.users = []

