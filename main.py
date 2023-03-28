from fastapi import FastAPI
from db import models
from db.database import engine
from routers.users import router as users_router
from routers.transactions import router as transactions_router


models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(users_router)
app.include_router(transactions_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
