from location import Location


class Event:
    def __init__(self, *args, **kwargs):
        # dovecot login success case
        if "dls" in kwargs:
            event = kwargs['dls']
            self.timestamp = event['@timestamp']
            self.email = event['source.user.email']
            self.hostname = event['host']['hostname']
            country = event['geoip']['country_name']
            try:
                city = event['geoip']['city_name']
            except KeyError:
                city = "null"
            ip = event['source.ip']
            self.location = Location(ip, country, city)

    def to_json(self):
        json = {

        }
        return json

    def __str__(self):
        return "timestamp: " + self.timestamp + "\nemail: " + self.email + "\ncountry: " + self.country + "\ncity: " + self.city + "\nip: " + self.ip + "\nhostname: " + self.hostname
