from email_validator import EmailNotValidError
from pydantic import validate_email


class EmailField(str):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value) -> str:
        try:
            validate_email(value)
            return value
        except EmailNotValidError:
            raise ValueError("Email is not valid")
