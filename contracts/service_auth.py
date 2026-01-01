from enum import Enum


class AuthServiceContract:
    ENV_URL = "AUTH_SERVICE_URL"

    class Endpoints(str, Enum):
        CREATE_CREDENTIALS = "/v1/auth/create_credentials"
        LOGIN = "/v1/auth/login"
        REFRESH = "/v1/auth/refresh"

        def __str__(self):
            return self.value