from fastapi import FastAPI
from app.routers.users import router as users_router
from app.routers.transactions import router as transactions_router
from app.config.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(users_router)
app.include_router(transactions_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
