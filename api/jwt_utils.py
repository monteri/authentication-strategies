import jwt
from datetime import datetime, timedelta
from django.conf import settings


def generate_token(payload, expiration_minutes=60):
    expiration_time = datetime.utcnow() + timedelta(minutes=expiration_minutes)
    payload['exp'] = expiration_time
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    return token


def verify_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
