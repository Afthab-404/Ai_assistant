from database.db import users

for user in users.find():
    print(user)