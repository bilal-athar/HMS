import datetime

from email_validator import validate_email, EmailNotValidError
from flask import *
from flask import Blueprint, jsonify

from flask_jwt_extended import create_access_token, jwt_required
from flask_mail import Mail, Message

from HMS.models.doctors import Doctors
from HMS import config
from HMS import create_app

db_users = Blueprint('db_users', __name__)

app = create_app()
secret_key = config.SECRET_KEY
security_password_salt = config.SECURITY_PASSWORD_SALT

mail_settings = {
    "MAIL_SERVER": config.MAIL_SERVER,
    "MAIL_PORT": config.MAIL_PORT,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": config.MAIL_USERNAME,
    "MAIL_PASSWORD": config.MAIL_PASSWORD
}
app.config.update(mail_settings)
mail = Mail(app)


def sendEmail(email, subject='Verification email', sender=config.MAIL_USERNAME,
              body="This is the verification email"):
    try:
        with app.app_context():
            msg = Message(subject=subject,
                          recipients=[email],
                          html=body,
                          sender=sender,
                          )
            mail.send(msg)
        return jsonify(message="Email sent!", category="success"), 200
    except Exception:
        return jsonify(message="something went wrong", category="error"), 400


@db_users.route('/register', methods=['GET', 'POST'])
def home():
    data = request.get_json()
    email = data['email']
    password = data['password']
    name = data['name']
    try:
        valid = validate_email(email)
        email = valid.email
    except EmailNotValidError:
        return jsonify(message='invalid email', category="error"), 400
    if not email or not password:
        return jsonify(message='email or password required', category="error"), 400
    if not name:
        return jsonify(message="name required", category="error"), 400
    if Doctors.objects(email=email).first() is not None:
        return jsonify(message="email already exist", category="error"), 400
    user_type = data["user_type"]
    if not user_type:
        return jsonify(message="user type required", category="error"), 400

    dbuser = Doctors()
    dbuser.name = name
    dbuser.email = email
    dbuser.user_type = user_type
    dbuser.hash_password(password)
    dbuser.save()

    auth_token = dbuser.generate_auth_token(expiration=600).decode('ascii')
    auth_url = "http://0.0.0.0:5000/verify_account?auth_token={}&email={}".format(
        auth_token, email)
    email_body = """<html>
                 <head>
                 <style>
                 .myButton {box-shadow: 0px 5px 14px -7px #276873;background-color:#599bb3;border-radius:42px;
                 display:inline-block;cursor:pointer;
                 color:#ffffff !important;font-family:Arial;font-size:20px;font-weight:bold; 
                 font-style:italic;padding:13px 32px;text-decoration:none;text-shadow:0px 1px 0px #3d768a;}
                 .myButton:hover {background-color:#408c99;}
                 .myButton:active {position:relative;top:1px;}
                 </style>
                 </head>
                 <body>
                 <p>Please click on the link below to verify your account</p><br>
                 <a class="myButton" href="%s">Verify Account</a>
                 </body>
                 </html>""" % auth_url
    sendEmail(email=email, body=email_body)
    print(auth_url)
    return jsonify(message="email verification sent, pLease check your email", category="success"), 200


@db_users.route('/resend_verification', methods=['GET', 'POST'])
def resend_verification_email():
    data = request.get_json()
    email = data['email']
    try:
        valid = validate_email(email)
        email = valid.email
    except EmailNotValidError:
        return jsonify(message='invalid email', category="error"), 400
    try:
        user = Doctors.objects(email=email)[0]
        # user_id = user.id
        email = user.email
        auth_token = user.generate_auth_token(expiration=600).decode('ascii')
        # print(auth_token)
        auth_url = "http://0.0.0.0:5000/?auth_token={}&email={}".format(
            auth_token, email)
        email_body = '<html>' \
                     '<body>' \
                     '<p>Please click on the link below to verify your account</p><br>' \
                     '<a href="{}">{}</a>' \
                     '</body>' \
                     '</html>'.format(auth_url, auth_url)
        sendEmail(email=email, body=email_body)
    except Exception:
        return jsonify(message="something went wrong, try putting valid email", category="error"), 400
    return jsonify(message="email verification sent, pLease check your email", category="success"), 200


@db_users.route('/verify_account', methods=['GET', 'POST'])
def verify_account():
    try:
        email = request.args.get('email')
        auth_token = request.args.get('auth_token')
        print(auth_token)
        user = Doctors.verify_auth_token(auth_token)
        return jsonify(message="email verification successful", category="success"), 200
    except Exception as e:
        return jsonify(message="something went wrong", category="error"), 400


@db_users.route('/login', methods=['GET', 'POST'])
def login():
    data = request.get_json(force=True)
    email = data["email"]
    password = data["password"]
    if not data["email"]:
        return jsonify(message="Email Required", category="error"), 400
    elif not data["password"]:
        return jsonify(message="Password Required", category="error"), 400
    else:
        if Doctors.objects(email=email):
            user = Doctors.objects(email=email)[0]
        else:
            return jsonify(message="user doesn't exist", category="error"), 400
        if not user.active:
            return jsonify(message="email not verified", category="error"), 400

    if Doctors.objects(email=email).first() is not None:
        if user.verify_password(password):
            expires = datetime.timedelta(days=7)
            access_token = create_access_token(identity=data['email'], expires_delta=expires)
            return jsonify(message="Login Succeeded!", access_token=access_token, category="success",
                           doctor_id=str(user.id), name=user.name, user_type=user.user_type), 200
        return jsonify(message="Bad Email or Password", category="error"), 400
    return jsonify(message="already logged in", category="error"), 400
