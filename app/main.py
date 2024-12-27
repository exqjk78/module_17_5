from fastapi import FastAPI
from app.routers import task
from app.routers import user

app = FastAPI()
app.include_router(task.router)
app.include_router(user.router)
