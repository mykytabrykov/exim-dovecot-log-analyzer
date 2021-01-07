from location import Location
import json
from types import SimpleNamespace


class Document:
    def __init__(self, event):
        self.document = json.loads(json.dumps(event), object_hook=lambda d: SimpleNamespace(**d))

    def to_json(self):
        return json.dumps(self.document, default=lambda x: x.__dict__, sort_keys=False, indent=4)

    def __str__(self):
        #return "timestamp: " + self.timestamp + "\nemail: " + self.email + "\ncountry: " + self.country + "\ncity: " + self.city + "\nip: " + self.ip + "\nhostname: " + self.hostname
        return str(self.document)
