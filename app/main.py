from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db import engine, Base
from app.routers.product import product_router
from app.routers.meal import meal_router


@asynccontextmanager
async def lifespan(app: FastAPI):
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
  yield
  await engine.dispose()
  

app = FastAPI(
  title='Calorie Calculator',
  description='It calculates calories',
  version='0.1',
  lifespan=lifespan
  )


app.include_router(meal_router)
app.include_router(product_router)