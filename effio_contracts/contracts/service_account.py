from enum import Enum


class AccountServiceContract:
    ENV_URL = "AUTH_SERVICE_URL"

    class V1(str, Enum):
        GET_BY_ID = "/v1/account/get_by_id"
        GET_ALL = "/v1/account/get_all"
        CREATE = "/v1/account/create"
        UPDATE = "/v1/account/update"
        DELETE = "/v1/account/delete"
        VERIFY_EMAIL = "/v1/account/verify_email"
        VERIFY_PHONE_NUMBER = "/v1/account/verify_phone_number"

        def __str__(self):
            return self.value
