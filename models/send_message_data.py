from pydantic import BaseModel

class SendMessage(BaseModel):
    email: str
    user_receiver_email: str
    message_body: str