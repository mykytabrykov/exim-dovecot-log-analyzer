from location import Location


class User:
    def __init__(self, *args, **kwargs):
        if "user" in kwargs:
            kwargs = kwargs['user']
            self.email = kwargs['email']
            self.hostname = kwargs['hostname']
            self.logins_success_locations = []
            for location in kwargs['logins']['success']['locations']:
                self.logins_success_locations.append(Location(location=location))

    def to_json(self):
        user_json = {
            "email": self.email,
            "hostname": self.hostname,
            "logins": {
                "success": {
                    "locations":
                        self.locations_to_json()
                }
            }
        }
        return user_json

    def locations_to_json(self):
        locations_json = []
        for location in self.logins_success_locations:
            locations_json.append(location.to_json())
        return locations_json

    def check_country(self, loc):
        for location in self.logins_success_locations:
            if location.hard_equals(loc):
                location.times += 1
                return True
            if location.soft_equals(loc):
                self.__add_new_location(loc)
                return True
        self.__add_new_location(loc)
        return False

    def __add_new_location(self, loc):
        self.logins_success_locations.append(loc)
