from document import Document
from new_event import NewDocument
MAX_RESPONSE_SIZE = "10"


class EventManager:
    def get_events(self, es_client, query, index):
        events = []
        res = es_client.search(index=index, body=query, size=MAX_RESPONSE_SIZE)

        if res['hits']['total']['value'] != 0:  # if there are some not analyzed docs
            event_list = res['hits']['hits'].copy()
            for i in range(len(event_list)):
                events.append(NewDocument(event_list[i]))
                # print("Log num.", i, event_list[i])
        return events
