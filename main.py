from fastapi import FastAPI

from db import models
from db.database import engine

from routers import auth_router, user_router

app = FastAPI()


app.include_router(auth_router.router)
app.include_router(user_router.router)


models.Base.metadata.create_all(bind=engine)
