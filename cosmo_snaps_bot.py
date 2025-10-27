import os
import random
import time
from dotenv import load_dotenv
import telegram
import schedule
from utils import logger


def send_image_to_telegram(bot, image_path: str, caption: str = None) -> None:
    """Отправляет изображение в Telegram-канал.

    Args:
        bot (telegram.Bot): Объект Telegram-бота.
        image_path (str): Путь к изображению для отправки.
        caption (str, optional): Подпись к изображению. По умолчанию None.

    Raises:
        OSError: При ошибках открытия файла.
        telegram.error.TelegramError: При ошибках отправки в Telegram.
    """
    if not isinstance(image_path, str):
        raise ValueError(f"Некорректный путь к изображению: {image_path}")
    with open(image_path, "rb") as photo:
        try:
            bot.send_photo(chat_id=os.getenv("TG_CHAT_ID"), photo=photo, caption=caption)
        except telegram.error.TelegramError as e:
            logger.error(f"Ошибка при отправке изображения {image_path} в Telegram: {e}")
            raise
    logger.info(f"Изображение отправлено: {image_path}")


def get_random_image_from_random_folder(image_dirs: list) -> str:
    """Выбирает случайную папку из списка и случайное изображение из неё.

    Args:
        image_dirs (list): Список путей к папкам с изображениями.

    Returns:
        str: Полный путь к выбранному изображению.

    Raises:
        ValueError: Если ни одна папка не найдена или в выбранной папке нет изображений.
        OSError: При ошибках доступа к файловой системе.
    """
    valid_extensions = (".jpg", ".png")

    existing_dirs = [d for d in image_dirs if os.path.exists(d)]
    if not existing_dirs:
        raise ValueError("Ни одна из указанных папок не найдена")