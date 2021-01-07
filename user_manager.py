from document import Document
import uuid

USERS_INDEX = "cpanel-users"


class UserManager:

    def __init__(self):
        self.users = []

    def get_user(self, event, es_client):
        for user in self.users:
            if user.document._source.email == event.document._source.source.user.email and user.document._source.hostname == event.document._source.host.hostname:
                # print("User already exist inside runtime users' list. Return his document to caller...")
                return user
        # user does not exist at runtime, need to be retrieved from es
        query = {
            "query": {
                "bool": {
                    "filter": {
                        "term": {"email.keyword": event.document._source.source.user.email}
                    }
                }
            }
        }
        res = es_client.search(index=USERS_INDEX, body=query)
        if res['hits']['total']['value'] != 0:  # user exist inside the index -> append and return it to caller method
            user = Document(user=res['hits']['hits'][0])
            self.users.append(user)  # append new user's document
            return user
        else:  # user does not exist, need to be created...
            new_user_json = {
                "_type": "_doc",
                "_index": USERS_INDEX,
                "_id": uuid.uuid4().__str__(),
                "_source": {
                    "email": event.document._source.source.user.email,
                    "hostname": event.document._source.host.hostname,
                    "login": {
                        "success": {
                            "locations": [{
                                "ip": event.document._source.source.ip,
                                "country": event.document._source.geoip.country_name,
                                #"city": event.document._source.geoip.city_name,
                                "counter": 1
                            }
                            ]
                        }
                    }

                }
            }
            user = Document(new_user_json)
            # print(new_user_json)
            self.users.append(user)
            return user

    def update_users(self):
        for user_doc in self.users:
            body = {
                "doc": user_doc.source.to_json(),
                'doc_as_upsert': "true"
            }
            res = self.es_client.update(index=user_doc.index, id=user_doc.id, body=body)
        # print("Update_users result: ", end="")
        # print(res)
