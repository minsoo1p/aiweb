import os

app_key = os.getenv('APP_KEY')
hash_method = os.getenv('HASH')
salt = int(os.getenv('SALT'))

print(app_key)
print(hash_method)
print(salt)