from pydantic import BaseModel


class BaseUser(BaseModel):
    email: str
    full_name: str
