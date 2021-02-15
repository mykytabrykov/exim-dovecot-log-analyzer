import uuid, datetime, os, time, configparser, logging
from elasticsearch_dsl import Search, connections
from es_client import EsClient
from pytz import timezone


class User:
    def __init__(self, email):
        self.__config = configparser.ConfigParser()
        self.__config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

        self.__es_client = EsClient().connect()
        connections.add_connection(conn=self.__es_client, alias="user")
        self.email = email
        self.profile = None

    def get_user(self):
        s = Search(index=self.__config['users']['index'], using='user') \
            .filter('term', email__keyword=self.email)

        response = s.execute()

        if len(response) > 0:
            for user in response:
                self.profile = user
                return self
        return None


    def create_empty_user(self):
        email = self.email
        hostname = 'none'
        score = 0.0001
        last_update = datetime.datetime.now(timezone('UTC')).isoformat()
        dovecot = {
            "login": {
                "success": {
                    "locations": []
                },
                "failure": {
                    "locations": []
                }
            }
        }

        exim = {
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

        new_user_body = {
            "last_update": last_update,
            "email": email,
            "hostname": hostname,
            "score": score,
            "dovecot": dovecot,
            "exim": exim,
        }
        print(new_user_body)
        res = self.__es_client.index(index=self.__config['users']['index'], id=uuid.uuid4().__str__(),
                                     body=new_user_body)
        # time needed by Elasticsearch ingestion
        time.sleep(1)
        return self.get_user()

    def update(self):
        self.profile.last_update = datetime.datetime.now(timezone('UTC')).isoformat()

        print(self.profile.to_dict())

        body = {
            "doc": self.profile.to_dict(),
            "doc_as_upsert": "true"
        }
        result = self.__es_client.update(index=self.profile.meta.index, id=self.profile.meta.id, body=body)
        print(result)
        if result['result'] == 'updated':
            logging.warning('User profile (' + self.profile.email + ') was successfully updated')
        else:
            logging.error('Occurred error during user profile (', self.profile.email, ') update')
