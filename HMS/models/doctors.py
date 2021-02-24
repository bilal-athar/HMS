import datetime

from mongoengine import ReferenceField
from passlib.apps import custom_app_context as pwd_context
from bson import ObjectId
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from HMS import config
from HMS.extensions.extensions import db


class Doctors(db.Document):
    name = db.StringField()
    email = db.EmailField()
    user_type = db.StringField()
    password = db.StringField()
    active = db.BooleanField(default=False)
    confirmed_at = db.DateTimeField()

    def hash_password(self, password):
        self.password = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

    def generate_auth_token(self, expiration=600):
        s = Serializer(config.SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': str(self.id)})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(config.SECRET_KEY)
        print(token)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return "Token Expired"
        except BadSignature:
            return "Invalid Token"
        print(type(ObjectId(data['id'])))
        user = Doctors.objects.get(id=ObjectId(data['id']))
        user.confirmed_at = datetime.datetime.now()
        user.active = True
        user.save()
        return user


class Patient(db.Document):
    doctor_id = db.ListField(ReferenceField('Doctors'))
    first_name = db.StringField()
    last_name = db.StringField()
    date = db.DateTimeField()
    age = db.StringField()
    disease_name = db.StringField()
    medicine_name = db.StringField()
    cnic = db.StringField()
    status = db.StringField()
