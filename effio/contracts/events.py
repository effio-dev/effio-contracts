from enum import Enum


class EventBusContract:
    # Common Event Detail Types
    class DetailTypes(str, Enum):
        ACCOUNT_CREATED = "AccountCreated"
        ACCOUNT_UPDATED = "AccountUpdated"
        ACCOUNT_DELETED = "AccountDeleted"

        def __str__(self):
            return self.value

    # Namespaces for sources
    class Sources:
        ACCOUNTS = "effio.accounts"
        AUTH = "effio.auth"
        PAYMENTS = "effio.payments"
