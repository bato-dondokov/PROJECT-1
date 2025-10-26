import asyncio
from aiogram import Bot
from config import MODEL_WEIGHTS, XRAYS_DIR, TEETH_DIR, DB_FILE
from xray2img import Xray2Teeth


"""Очередь на использование модели"""


model = Xray2Teeth(MODEL_WEIGHTS)
inference_queue = asyncio.Queue()


async def model_worker(bot: Bot):
    """Реализует очередь на использование модели YOLO"""
    while True:
        model.XRAY_FILE, model.TEETH_DIR = await inference_queue.get()

        try:
            model.process()
        except Exception as e:
            await bot.send_message(f"Ошибка очереди")
            print((f"Ошибка очереди: {e}"))
        finally:
            inference_queue.task_done()