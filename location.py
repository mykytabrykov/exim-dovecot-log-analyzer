class Location:
    def __init__(self, *args, **kwargs):
        if "location" in kwargs:
            location = kwargs['location']
            self.ip = location['source.ip']
            self.country = location['country']
            try:
                self.city = location['city']
            except KeyError:
                self.city = "null"
            try:
                self.times = location['times']
            except KeyError:
                self.times = 1

    def hard_equals(self, other):
        if isinstance(other, Location) and self.country == other.country and self.ip == other.ip and self.city == other.city:
            return True
        return False

    def soft_equals(self, other):
        if isinstance(other, Location) and self.country == other.country:
            return True
        return False

    def to_json(self):
        json = {
            "source.ip": self.ip,
            "country": self.country,
            "city": self.city,
            "times": self.times
        }
        return json
