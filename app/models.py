from sqlalchemy import Column, Integer, Float, String

from app.db import Base

class ProductTable(Base):
  __tablename__ = 'products'

  product_id = Column(Integer, primary_key=True, index=True)
  product_name = Column(String(50))
  calories = Column(Integer)
  protein = Column(Float)
  fats = Column(Float)
  carbs = Column(Float)



class MealTable(Base):
  __tablename__ = 'meal'

  meal_id = Column(Integer, primary_key=True, index=True)
  meal_name = Column(String(50))
  calories = Column(Integer)
  protein = Column(Float)
  fats = Column(Float)
  carbs = Column(Float)

  portions = Column(Integer)


