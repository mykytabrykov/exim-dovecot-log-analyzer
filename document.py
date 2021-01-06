from event import Event
from user import User

class Document:
    def __init__(self, *args, **kwargs):
        if "event" in kwargs:
            kwargs = kwargs['event']
            self.context = "event"
            self.event = Event(event=kwargs['_source'])
        if "user" in kwargs:
            kwargs = kwargs['user']
            self.context = "user"
            self.user = User(user=kwargs['_source'])
        self.index = kwargs['_index']
        self.type = kwargs['_type']
        self.id = kwargs['_id']

    def __str__(self):
        return "index: " + self.index + "\ntype: " + self.type + "\nid: " + self.id

    def user_json_representation(self):  # changing context from event to user
        if self.context == "event":
            user_source = {
                "email": self.event.email,
                "hostname": self.event.hostname,
                "logins": {
                    "success": {
                        "locations":
                            [{
                                "source.ip": self.event.location.ip,
                                "country": self.event.location.country,
                                "city": self.event.location.city,
                                "times": 1
                            }]
                    }
                }
            }
            return user_source
