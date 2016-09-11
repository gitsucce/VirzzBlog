import os

##### GENERATE SECRET KEY #####
with open('.ICore_secret_key', 'a+') as secret:
    secret.seek(0)
    key = secret.read()
    if not key:
        key = os.urandom(64)
        secret.write(key)
        secret.flush()

##### SERVER SETTINGS #####
SECRET_KEY = key
SESSION_COOKIE_NAME = "session"
SESSION_TYPE = "filesystem"
SESSION_FILE_DIR = "/tmp/flask_session"
SESSION_COOKIE_HTTPONLY = True
PERMANENT_SESSION_LIFETIME = 604800  # 7 days in seconds

SQLALCHEMY_TRACK_MODIFICATIONS = True

SQLALCHEMY_DATABASE_URI = 'mysql://username:password@127.0.0.1:3306/youdbname'
DOMAIN = "www.yourdomain.com"
SCHEME = "http"
HOST = SCHEME+"://"+DOMAIN
