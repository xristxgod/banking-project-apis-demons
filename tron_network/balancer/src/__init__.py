from .middleware import UserMiddleware, user_middleware
from .inc import core
from config import Config


admin = await user_middleware(address=Config.ADMIN_WALLET_ADDRESS, private_key=Config.ADMIN_WALLET_PRIVATE_KEY)


__all__ = [
    "admin",
    "core",
    "UserMiddleware", "user_middleware",
]
