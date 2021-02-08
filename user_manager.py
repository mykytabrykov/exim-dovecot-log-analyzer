from testing import serializer
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
    def __init__(self):
        self.__config = configparser.ConfigParser()
        self.__config.read(os.path.join(os.path.dirname(__file__), 'config', 'config.ini'))
        self.__es_client = EsClient().connect()
        connections.add_connection(conn=self.__es_client, alias="user")
        self.users = []

    def get_user(self, email):
        for user in self.users:
            if user.email == email:
                # print("User already exist inside runtime users' list. Return his document to caller...")
                return user
        # user does not exist at runtime, need to be retrieved from elasticsearch
        s = Search(index=self.__config['users']['index'], using='user') \
            .filter('term', email__keyword=email)
        # print(s.to_dict())
        response = s.execute()
        for user in response:
            self.users.append(user)
            return user
        return None

    def create_empty_user(self, email):
        new_user_json = {
            "_type": "user",
            "_index": self.__config['users']['index'],
            "_id": uuid.uuid4().__str__(),
            "_source": {
                "last_update": datetime.datetime.now(timezone('UTC')).isoformat(),
                "email": email,
                "hostname": 'none',
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
                    "auth": 'none',
                    "emails": {
                        "sent": {
                            "total": 0,
                            "daily": []
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
        res = self.__es_client.index(index=new_user_json['_index'], id=new_user_json['_id'],
                                     body=new_user_json['_source'])
        # time needed by Elasticsearch ingestion
        time.sleep(1)
        return self.get_user(email)

    def update_users(self):
        for user in self.users:
            user.last_update = datetime.datetime.now(timezone('UTC')).isoformat()
            user_dict = user.to_dict()
            print(user_dict)
            body = {
                "doc": serializer.to_json(user_dict),
                "doc_as_upsert": "true"
            }
            self.__es_client.update(index=user.meta.index, id=user.meta.id, body=body)
            self.users = []
