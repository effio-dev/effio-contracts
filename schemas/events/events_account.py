from pydantic import BaseModel
import uuid


class AccountCreatedEvent(BaseModel):
    account_id: uuid.UUID
    email: str
    first_name: str