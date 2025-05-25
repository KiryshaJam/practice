import os
from dotenv import load_dotenv

load_dotenv()
 
# Конфигурация базы данных SQLite
SQLALCHEMY_DATABASE_URI = 'sqlite:///cars.db' 