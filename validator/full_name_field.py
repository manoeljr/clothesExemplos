

class FullNameField(str):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        try:
            first_name, last_name = value.split()
            return value
        except Exception:
            raise ValueError("You should provide at least 2 names")
