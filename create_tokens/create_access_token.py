from datetime import datetime, timedelta
from decouple import config

import jwt


def create_access_token(user):
    try:
        payload = {"sub": user["id"], "exp": datetime.utcnow() + timedelta(minutes=120)}
        return jwt.encode(payload, config("JWT_SECRET"), algorithm="HS256")
    except Exception as ex:
        raise
