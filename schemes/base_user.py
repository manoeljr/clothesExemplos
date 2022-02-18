from email_validator import EmailNotValidError
from pydantic import BaseModel, validator, validate_email


class BaseUser(BaseModel):
    email: str
    full_name: str

    @validator("email")
    def valida_email(cls, value):
        try:
            validate_email(value)
            return value
        except EmailNotValidError:
            raise ValueError("Email is not valid")

    @validator("full_name")
    def valida_full_name(cls, value):
        try:
            first_name, last_name = value.split()
        except Exception:
            raise ValueError("You should provide at least 2 names")
