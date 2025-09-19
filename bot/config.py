from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

"""Конфигурационный файл"""

"""Токен телеграмм-бота"""
TOKEN='YOUR_TOKEN'  

"""Путь до модели обнаружения объектов"""
MODEL_WEIGHTS = "bot/models/YOLO11n-obb(main)/weights/best.pt"

"""Путь до директории для снимков"""
XRAYS_DIR = "bot/xrays/"

"""Путь до директории для изображений зубов"""
TEETH_DIR = "bot/teeth/"

"""Путь до файла БД"""
DB_FILE = "bot/db.sqlite3"

"""Пароли для авторизации пользователей"""
EXPERT_PASSWORD='YOUR_PASSWORD'
ADMIN_PASSWORD='YOUR_PASSWORD'

"""Названия классов разметки по умолчанию"""
DEFAULT_LABELS={
    1:"Здоровый зуб", 
    2:'Кариес', 
    3:'Пульпит',
    4:'Периодонтит',
    5:'Сомневаюсь в ответе'
}

"""Названия рекомендаций по умолчанию"""
DEFAULT_RECOMMENDATIONS={
    1:"Лечить", 
    2:'Удалять', 
    3:'Наблюдать',
    4:'Сомневаюсь в ответе'
}

"""Коэффициенты для обрезки снимка."""
OBB_SCALE = 2.0 # Масштаб учеличения размеров ограничивающей рамки
CROP_WIDTH = 180 # Ширина обрезанного снимка
CROP_LENGTH = 220 # Длина обрезанного снимка