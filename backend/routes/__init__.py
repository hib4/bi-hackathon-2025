from .auth_router import router as auth_router
from .user_router import router as user_router
from .book_router import router as book_router

routers = [
    auth_router,
    user_router,
    book_router
]