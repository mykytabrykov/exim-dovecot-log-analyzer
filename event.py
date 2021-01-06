from location import Location

class Event:
    def __init__(self, *args, **kwargs):
        if "event" in kwargs:
            kwargs = kwargs['event']
            self.timestamp = kwargs['@timestamp']
            self.email = kwargs['source.user.email']
            country = kwargs['geoip']['country_name']
            try:
                city = kwargs['geoip']['city_name']
            except KeyError:
                city = "null"
            ip = kwargs['source.ip']
            self.hostname = kwargs['host']['hostname']
            self.location = Location(ip, country, city)

    def to_json(self):
        event_json = {

        }
        return event_json


    def __str__(self):
        return "timestamp: " + self.timestamp + "\nemail: " + self.email + "\ncountry: " + self.country + "\ncity: " + self.city + "\nip: " + self.ip + "\nhostname: " + self.hostname
