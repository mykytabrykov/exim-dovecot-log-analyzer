import configparser
import os
from elasticsearch import Elasticsearch
from elasticsearch_dsl import connections


class EsClient:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), 'config', 'config.ini'))
        es_config = config['elasticsearch']

        self.server = es_config['server']
        self.port = es_config['port']
        self.protocol = es_config['protocol']
        self.username = es_config['username']
        self.password = es_config['password']
        self.ssl = es_config.getboolean('ssl')
        self.verify_certs = es_config.getboolean('verify_certs')

    def connect(self):
        try:
            client = Elasticsearch(self.server,
                                   http_auth=(self.username, self.password),
                                   scheme=self.protocol,
                                   port=self.port,
                                   use_ssl=self.ssl,
                                   verify_certs=self.verify_certs)
        except Exception as error:
            print("[EsConfig] Elasticsearch connection error, please verify settings:", error)
            return None
        return client
