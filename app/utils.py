# library imports
# pip install "passlib[bcrypt]"
from passlib.context import CryptContext
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi.encoders import jsonable_encoder
import json
from bson import ObjectId

conf = ConnectionConfig(
    MAIL_USERNAME="hello@uniorx.com",
    MAIL_PASSWORD="uniorx@plastk",
    MAIL_FROM="hello@uniorx.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_FROM_NAME="Hussnain",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER="app/templates"
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def password_reset(subject: str, email_to: str, body: dict):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        template_body=body,
        subtype='html',
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name='password_reset.html')
    print('Email sent')


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)
