from pydantic import BaseModel

class BlockUserData(BaseModel):
    is_admin: bool
    blocked_user: str