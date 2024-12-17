from drf_spectacular.extensions import OpenApiAuthenticationExtension


class MyAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "knox.auth.TokenAuthentication"
    name = "KnoxTokenAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": (
                "Token-based authentication with Knox. "
                "Include `Token <your-token>` in the `Authorization` header."
            ),
        }
