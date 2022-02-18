from datetime import datetime
from typing import Optional

from schemes.base_user import BaseUser


class UserSignOut(BaseUser):
    phone: Optional[str]
    created_at: datetime
    last_modified_at: datetime
