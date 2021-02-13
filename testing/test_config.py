import configparser

from user import User

user = User('j.shaw@utixo.co.uk')

print(user.profile.score)

user.profile.score = 2
print(user.profile.score)
user.update()