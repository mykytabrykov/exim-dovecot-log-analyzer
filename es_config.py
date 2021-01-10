from elasticsearch import Elasticsearch


class EsConfig:
    def __init__(self):
        es_server = 'linoc.utixo.net'
        es_port = 29200
        es_protocol = 'https'
        es_login = 'elastic'
        es_password = 'lfos8PQlplAHQYaKoCBl'
        es_ssl = True
        es_verify_certs = True
        try:
            self.es_client = Elasticsearch(es_server,
                                           http_auth=(es_login, es_password),
                                           scheme=es_protocol,
                                           port=es_port,
                                           use_ssl=es_ssl,
                                           verify_certs=es_verify_certs)
        except Exception as er:
            print("[ElasticsearchClient] connection error:", er)

    def get_es_client(self):
        return self.es_client
