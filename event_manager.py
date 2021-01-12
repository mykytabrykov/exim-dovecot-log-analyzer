import serializer


class EventManager:
    def __init__(self, es_client, max_response_size):
        self.events = []
        self.es_client = es_client
        self.max_response_size = max_response_size

    def get_events(self, query, index):
        res = self.es_client.search(index=index, body=query, size=self.max_response_size)

        if res['hits']['total']['value'] != 0:  # if there are some not analyzed docs
            event_list = res['hits']['hits'].copy()
            for i in range(len(event_list)):
                self.events.append(serializer.to_simple_namespace(event_list[i]))
                # print("Log num.", i, event_list[i])
        return self.events


    def update_and_flush(self):
        self.__update()
        self.__flush()

    def __update(self):
        for event in self.events:
            body = {
                "doc": {
                    "python": {
                        "analyzed": "true"
                    }
                }
            }
            self.es_client.update(index=event._index, id=event._id, body=body)

    def __flush(self):
        self.events.clear()