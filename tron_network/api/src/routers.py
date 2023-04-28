from fastapi import APIRouter

from .apps.admin import views as admin_views

router = APIRouter()

router.include_router(admin_views.router, prefix='/admin', tags=['Admin'])
