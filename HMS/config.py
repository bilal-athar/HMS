import os

DEBUG = True
HOST = 'localhost'

SECRET_KEY = os.environ.get("SECRET_KEY")
DB_SETTINGS = {
    'DB_NAME': os.environ.get('DB_NAME'),
    'DB_PORT': os.environ.get('DB_PORT'),
    'DB_HOST': os.environ.get('DB_HOST')
}
SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT')

MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_PORT = os.environ.get('MAIL_PORT')
MAIL_SERVER = os.environ.get('MAIL_SERVER')

MAIL_SETTINGS = {
    'MAIL_SERVER': os.environ.get('MAIL_SERVER'),
    'MAIL_PORT': os.environ.get('MAIL_PORT'),
    'MAIL_USE_TLS': os.environ.get('MAIL_USE_TLS'),
    'MAIL_USE_SSL': os.environ.get('MAIL_USE_SSL'),
    'MAIL_USERNAME': os.environ.get('MAIL_USERNAME'),
    'MAIL_PASSWORD': os.environ.get('MAIL_PASSWORD')
}