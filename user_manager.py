import serializer
import uuid
import datetime

USERS_INDEX = "users-cpanel"


class UserManager:

    def __init__(self, es_client):
        self.users = []
        self.es_client = es_client

    def get_user(self, event):
        for user in self.users:
            if user._source.email == event._source.source.user.email and user._source.hostname == event._source.host.hostname:
                # print("User already exist inside runtime users' list. Return his document to caller...")
                return user
        # user does not exist at runtime, need to be retrieved from es
        query = {
            "query": {
                "bool": {
                    "filter": {
                        "term": {"email.keyword": event._source.source.user.email}
                    }
                }
            }
        }
        res = self.es_client.search(index=USERS_INDEX, body=query)
        if res['hits']['total']['value'] != 0:  # user exist inside the index -> append and return it to caller method
            user = serializer.to_simple_namespace(res['hits']['hits'][0])
            self.users.append(user)  # append new user's document
            return user
        else:  # user does not exist, need to be created...
            new_user_json = {
                "_type": "_doc",
                "_index": USERS_INDEX,
                "_id": uuid.uuid4().__str__(),
                "_source": {
                    "last_update": datetime.datetime.now().isoformat(),
                    "email": event._source.source.user.email,
                    "hostname": event._source.host.hostname,
                    "login": {
                        "success": {
                            "locations": [
                            ]
                        },
                        "failure": {
                            "locations": [
                            ]
                        }
                    }
                }
            }
            user = serializer.to_simple_namespace(new_user_json)
            # print(new_user_json)
            self.users.append(user)
            return user

    def dump(self):
        for user in self.users:
            timestamp = (datetime.datetime.now() - datetime.timedelta(hours=1)).replace(microsecond=0).isoformat()
            timestamp += ".000Z"
            user._source.last_update = timestamp
            body = {
                "doc": serializer.to_json(user._source),
                "doc_as_upsert": "true"
            }
            res = self.es_client.update(index=user._index, id=user._id, body=body)

