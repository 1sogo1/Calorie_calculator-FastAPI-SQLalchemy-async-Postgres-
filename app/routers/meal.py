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


@meal_router.post('/create_meal', response_model=MealSchema)
async def create_meal(application: CreatMealSchema, db: AsyncSession = Depends(get_db)):
    nutrients = {
        'calories': 0,
        'protein': 0,
        'fats': 0,
        'carbs': 0
    }

    product_ids = [int(pid) for pid in application.product_id_n_val.keys()]
    products_query = select(ProductTable).where(ProductTable.product_id.in_(product_ids))
    products = dict(await db.execute(products_query))
    
    for product_id, gramm in application.product_id_n_val.items():
        product_id_int = int(product_id)
        
        if product_id_int not in products:
            raise HTTPException(status_code=404, detail=f'Продукт не найден: {product_id}')
            
        product = products[product_id_int]
        rate = gramm / 100
        
        nutrients['calories'] += int(product.calories * rate / application.portions)
        nutrients['protein'] += product.protein * rate / application.portions
        nutrients['fats'] += product.fats * rate / application.portions
        nutrients['carbs'] += product.carbs * rate / application.portions
    
    meal = MealTable(
        meal_name=application.meal_name,
        **nutrients,
        portions=application.portions
    )
    
    try:
        db.add(meal)
        await db.commit()
        await db.refresh(meal)
        return meal
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f'Ошибка при создании блюда: {str(e)}')

  

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