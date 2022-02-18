from typing import Optional

from pydantic import BaseModel

from validator.email_field import EmailField
from validator.full_name_field import FullNameField


class BaseUser(BaseModel):
    email: EmailField
    full_name: Optional[FullNameField]
