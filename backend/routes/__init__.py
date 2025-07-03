from .router import router as gptRouter
from .authRouter import router as authRouter
from .userRouter import router as userRouter

routers = [
    gptRouter,
    authRouter,
    userRouter
]