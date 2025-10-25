from fastapi import APIRouter, HTTPException, Depends, Query
from app.schemas import ProductSchema
from app.db import AsyncSession, get_db
from app.models import ProductTable
from typing import Optional
from sqlalchemy import select

product_router = APIRouter(prefix='/products', tags=['Продукты'])

@product_router.post('/add_product')
async def add_product(product: ProductSchema, db: AsyncSession = Depends(get_db)):
  new_product = ProductTable(
    product_name = product.product_name,
    calories = product.calories,
    protein = product.protein,
    fats = product.fats,
    carbs = product.carbs
  )

  db.add(new_product)
  try:
    await db.commit()
    await db.refresh(new_product)
  except Exception as e:
    await db.rollback()
    raise HTTPException(status_code=400, detail=f'something went wrong: {str(e)}')
  
  return {'message': f'{product.product_name} добавлен'}


@product_router.get('/get_products')
async def get_products(
  db: AsyncSession = Depends(get_db), 
  id: Optional[str] = Query(None, description='id продукта, опционально') 
  ):
  if id is not None:
    result = await db.execute(select(ProductTable).where(ProductTable.product_id == id))
    exact_product = result.scalars().first()
    if not exact_product:
      raise HTTPException(status_code=404, detail='this product does not exist')
    
    return exact_product

  else:
    result = await db.execute(select(ProductTable))
    all_prodcts = result.scalars().all()

    return all_prodcts
  

@product_router.delete('/delete_product/{id}')
async def delete_product(id: str, db: AsyncSession = Depends(get_db)):
  result = await db.execute(select(ProductTable).where(ProductTable.product_id == id))
  product_to_delete = result.scalars().first()
  if not product_to_delete:
    raise HTTPException(status_code=404, detail='this product does not exist')
  
  try:
    await db.commit()
    await db.delete(product_to_delete)
  except Exception as e:
    await db.rollback()
    raise HTTPException(status_code=400, detail=f'something went wrong {str(e)}')
  
  return {'message': 'peoduct is deleted'}


@product_router.put('/update_product/{id}')
async def update_product(product: ProductSchema, id: int, db: AsyncSession = Depends(get_db)):
  result = await db.execute(select(ProductTable).where(ProductTable.product_id == id))
  product_to_update = result.scalars().first()
  if not product_to_update:
    raise HTTPException(status_code=404, detail='this product does not exist')
  
  product_to_update.product_name = product.product_name
  product_to_update.calories = product.calories
  product_to_update.protein = product.protein
  product_to_update.fats = product.fats
  product_to_update.carbs = product.carbs

  try:
    await db.commit()
    await db.refresh(product_to_update)
  except Exception as e:
    await db.rollback()
    raise HTTPException(status_code=400, detail=f'something went wrong {str(e)}')
  
  return {'message': f'{product_to_update.product_name} is updated'}

