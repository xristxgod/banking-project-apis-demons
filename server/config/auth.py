from starlette.requests import Request
from starlette.datastructures import FormData
from sqladmin.authentication import AuthenticationBackend

import settings

__all__ = (
    'get_authentication_backend',
)


class AdminAuthenticationBackend(AuthenticationBackend):
    credentials = settings.ADMIN_CREDENTIALS

    @classmethod
    def is_form_valid(cls, form: FormData) -> bool:
        return (
            form['username'] == cls.credentials['username'] and
            form['password'] == cls.credentials['password']
        )

    @classmethod
    def generate_token(cls, request: Request) -> str:
        # TODO
        return 'token'

    @classmethod
    def is_token_valid(cls, request: Request) -> bool:
        if token := request.session.get('token'):
            return True
        return False

    async def login(self, request: Request) -> bool:
        if self.is_form_valid(form=await request.form()):
            request.session.update({'token': self.generate_token(request=request)})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        if self.is_token_valid(request=request):
            return True
        return False


def get_authentication_backend(backend_name: str):
    if not settings.USE_AUTHORISATIONS[backend_name]:
        return None

    match backend_name:
        case 'swagger':
            return
        case 'admin':
            return AdminAuthenticationBackend(secret_key=settings.BACKEND_SECRET_KEY)
        case 'admin-exchange-rate':
            return AdminAuthenticationBackend(secret_key=settings.BACKEND_SECRET_KEY)
