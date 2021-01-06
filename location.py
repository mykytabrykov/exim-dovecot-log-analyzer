class Location:
    def __init__(self, *args, **kwargs):
        if "location" in kwargs:
            kwargs = kwargs['location']
            self.ip = kwargs['source.ip']
            self.country = kwargs['country']
            try:
                self.city = kwargs['city']
            except KeyError:
                self.city = "null"
            try:
                self.times = kwargs['times']
            except KeyError:
                self.times = 1
        elif args:
            self.ip = args[0]
            self.country = args[1]
            self.city = args[2]
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
        location_json = {
            "source.ip": self.ip,
            "country": self.country,
            "city": self.city,
            "times": self.times
        }
        return location_json
