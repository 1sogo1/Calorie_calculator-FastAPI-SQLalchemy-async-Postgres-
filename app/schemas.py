from pydantic import BaseModel, Field
from typing import Dict

class ProductSchema(BaseModel):
  product_name: str = Field(..., min_length=1, max_length=50, description='Название продукта')

  calories: int = Field(..., ge=1, description='Калории на 100г')
  protein: float = Field(..., description='Белок на 100г')
  fats: float = Field(..., description='Жиры на 100г')
  carbs: float = Field(..., description='Углеводы на 100г')


class MealSchema(BaseModel):
  meal_id: int
  meal_name: str
  
  calories: int = Field(..., ge=1, description='Калории на 100г')
  protein: float = Field(..., description='Белок на 100г')
  fats: float = Field(..., description='Жиры на 100г')
  carbs: float = Field(..., description='Углеводы на 100г')

  class Config:
    orm_mode = True

class CreateMealSchema(BaseModel):
  meal_name: str = Field(..., min_length=1, max_length=50, description='Название блюда')

  product_id_n_val: Dict[str, int] = Field(
    ..., 
    example={"1": 100, "2": 200}, 
    description='id продуктов и его граммовки в блюде, например: {1: 1000, 2: 400}'
    )

  portions: int = Field(..., ge=1, description='количество порций')

