from event import Event
from user import User


class Document:
    def __init__(self, *args, **kwargs):
        if "dovecot-login-success" in kwargs:
            self.type = "dovecot-login-success"
            kwargs = kwargs['dovecot-login-success']
            self.source = Event(dls=kwargs['_source'])
        if "user" in kwargs:
            kwargs = kwargs['user']
            self.type = "user"
            self.source = User(user=kwargs['_source'])

        self.index = kwargs['_index']
        self.id = kwargs['_id']

    def user_json_representation(self):  # changing context from event to user
        if self.type == "event":
            user_source = {
                "email": self.source.email,
                "hostname": self.source.hostname,
                "dovecot": {
                    "login": {
                        "success": {
                            "locations":
                                [{
                                    "source.ip": self.source.location.ip,
                                    "country": self.source.location.country,
                                    "city": self.source.location.city,
                                    "times": 1
                                }]
                        },
                        "failure": {

                        }
                    }
                },
                "exim": {

                }
            }
            return user_source

    def __str__(self):
        return "index: " + self.index + "\ntype: " + self.type + "\nid: " + self.id
