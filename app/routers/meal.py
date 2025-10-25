from fastapi import APIRouter, HTTPException, Depends, Query
from app.schemas import MealSchema, CreatMealSchema
from app.db import AsyncSession, get_db
from app.models import MealTable, ProductTable
from typing import Optional
from sqlalchemy import select


meal_router = APIRouter(
  prefix='/meal',
  tags=['блюда']
)


@meal_router.post('/create_meal', response_model= MealSchema)
async def create_meal(application: CreatMealSchema, db: AsyncSession = Depends(get_db)):
  final_meal = {'calories': 0, 'protein': 0, 'fats': 0, 'carbs': 0}
  for product_id_str, gramm in application.product_id_n_val.items():
    try:
      product_id = int(product_id_str) 
    except ValueError:
      raise HTTPException(status_code=400, detail=f"Invalid product_id: {product_id_str}")

    result = await db.execute(select(ProductTable).where(ProductTable.product_id == product_id))
    product_to_use = result.scalars().first()

    if not product_to_use:
      raise HTTPException(status_code=404, detail='no product to use')
    
    rate = gramm / 100

    final_meal['calories'] += int(product_to_use.calories * rate / application.portions)
    final_meal['protein'] += product_to_use.protein * rate / application.portions
    final_meal['fats'] += product_to_use.fats * rate / application.portions
    final_meal['carbs'] += product_to_use.carbs * rate / application.portions

  go_to_db = MealTable(
    meal_name = application.meal_name,
    calories = int(final_meal['calories']),
    protein = round(final_meal['protein'], 1),
    fats = round(final_meal['fats'], 1),
    carbs = round(final_meal['carbs'], 1),
    portions = application.portions
  )

  db.add(go_to_db)
  try:
    await db.commit()
    await db.refresh(go_to_db)
    return go_to_db
  except Exception as e:
    await db.rollback()
    raise HTTPException(status_code=400, detail=f'something went wrong: {str(e)}')
  

@meal_router.get('/view')
async def get_meal(
  db: AsyncSession = Depends(get_db), 
  id: Optional[int] = Query(None, description='id блюда, опционально')
  ):
  if id is not None:
    result = await db.execute(select(MealTable).where(MealTable.meal_id == id))
    exact_meal = result.scalars().first()
    
    if not exact_meal:
      raise HTTPException(status_code=404, detail='not found')
    
    return exact_meal
  
  else:
    result = await db.execute(select(MealTable))
    all = result.scalars().all()
    if not all:
      raise HTTPException(status_code=404, detail='not found')

    return all
  

@meal_router.patch('/eat_one_or_more')
async def eat_one_or_more(
  id: int, 
  db: AsyncSession = Depends(get_db), 
  value: Optional[int] = Query(None, description='кол-во порций, по умолчанию 1')):
  result = await db.execute(select(MealTable).where(MealTable.meal_id == id))
  to_eat = result.scalars().first()

  if not to_eat:
    raise HTTPException(status_code=404, detail='does not exist')
  
  if value is not None and value > 0:
    to_eat.portions -= value
    v = value
  else:
    to_eat.portions -= 1
    v = 1
    
  try:
    await db.commit()
    await db.refresh(to_eat)
  except Exception as e:
    await db.rollback()
    raise HTTPException(status_code=400, detail=f'something went wrong {str(e)}')
  
  return {'message': f'you ate {v} porion(s) of {to_eat.meal_name}'}

@meal_router.delete('/delete_meal')
async def delete_meal(id: int, db: AsyncSession = Depends(get_db)):
  result = await db.execute(select(MealTable).where(MealTable.meal_id == id))
  to_delete = result.scalars().first()

  if not to_delete:
    raise HTTPException(status_code=404, detail='does not exist')
  
  name = to_delete.meal_name
  
  try:
    await db.delete(to_delete)
    await db.commit()
  except Exception as e:
    await db.rollback()
    raise HTTPException(status_code=400, detail=f'something went wrong {str(e)}')
  
  return {'message': f'{name} is deleted'}