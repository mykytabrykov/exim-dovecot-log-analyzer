from document import Document

DOVECOT_USERS_INDEX = "cpanel-users"


class UserManager:

    def __init__(self):
        self.users = []

    def get_user(self, log):
        for user_doc in self.users:
            if user_doc.source.email == log.source.email and user_doc.source.hostname == log.source.hostname:
                # print("User already exist inside runtime users' list. Return his document to caller...")
                return user_doc
        # user does not exist at runtime, need to be retrieved from es
        query = {
            "query": {
                "bool": {
                    "filter": {
                        "term": {"email.keyword": log.source.email}
                    }
                }
            }
        }
        res = self.es_client.search(index=DOVECOT_USERS_INDEX, body=query)
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


    def update_users(self):
        for user_doc in self.users:
            body = {
                "doc": user_doc.source.to_json(),
                'doc_as_upsert': "true"
            }
            res = self.es_client.update(index=user_doc.index, id=user_doc.id, body=body)
        # print("Update_users result: ", end="")
        # print(res)