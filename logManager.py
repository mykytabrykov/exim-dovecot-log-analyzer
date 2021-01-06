from document import Document

MAX_RESPONSE_SIZE = "10"


class LogManager:

    def get_logs(self, es_client, query, index):
        logs = []
        res = es_client.search(index=index, body=query, size=MAX_RESPONSE_SIZE)

        if res['hits']['total']['value'] != 0:  # if there are some not analyzed docs
            event_list = res['hits']['hits'].copy()
            for i in range(len(event_list)):
                logs.append(Document(event=event_list[i]))
                # print("Log num.", i, event_list[i])
        return logs
