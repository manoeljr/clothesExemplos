from typing import Optional

import databases
import jwt
import uvicorn
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.requests import Request

from enums.color_enum import ColorEnum
from enums.size_enum import SizeEnum

import sqlalchemy
from fastapi import FastAPI, HTTPException, Depends

from decouple import config

from schemes.users_sign_in import UserSignIn

from passlib.context import CryptContext

from create_tokens.create_access_token import create_access_token


DATABASE_URL = f"postgresql://" \
               f"{config('DB_USER')}:" \
               f"{config('DB_PASSWORD')}@" \
               f"{config('DB_SERVER')}:" \
               f"{config('DB_PORT')}/" \
               f"{config('DB_DATABASE')}"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("email", sqlalchemy.String(120), unique=True),
    sqlalchemy.Column("password", sqlalchemy.String(255)),
    sqlalchemy.Column("full_name", sqlalchemy.String(200)),
    sqlalchemy.Column("phone", sqlalchemy.String(13)),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column(
        "last_modified_at",
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
    ),
)

clothes = sqlalchemy.Table(
    "clothes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(120)),
    sqlalchemy.Column("color", sqlalchemy.Enum(ColorEnum), nullable=False),
    sqlalchemy.Column("size", sqlalchemy.Enum(SizeEnum), nullable=False),
    sqlalchemy.Column("photo_url", sqlalchemy.String(255)),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column(
        "last_modified_at",
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
    ),
)


class CustomHttpBearer(HTTPBearer):

    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        res = await super().__call__(request)
        try:
            payload = jwt.decode(res.credentials, config("JWT_SECRET"), algorithms=["HS256"])
            user = await database.fetch_one(users.select().where(users.c.id == payload["sub"]))
            request.state.user = user
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(401, "Token is expired")
        except jwt.InvalidTokenError:
            raise HTTPException(401, "Invalid token")


oauth2_scheme = CustomHttpBearer()


app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get(
    "/clothes/",
    dependencies=[
        Depends(oauth2_scheme)
    ]
)
async def get_all_clothes(request: Request):

    return await database.fetch_all(clothes.select())


@app.post("/register/")
async def create_user(user: UserSignIn):
    user.password = pwd_context.hash(user.password)
    query = users.insert().values(**user.dict())
    cod = await database.execute(query)
    new_user = await database.fetch_one(users.select().where(users.c.id == cod))
    token = create_access_token(new_user)
    return {"token": token}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
