from .auth_router import router as auth_router
from .user_router import router as user_router
from .book_router import router as book_router
from .voice_router import router as voice_router
from .analytic_router import router as analytic_router

routers = [
    auth_router,
    user_router,
    book_router,
    voice_router,
    analytic_router
]