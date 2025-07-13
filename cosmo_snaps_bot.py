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

    try:
        with open(image_path, "rb") as photo:
            try:
                bot.send_photo(chat_id=os.getenv("TG_CHAT_ID"), photo=photo, caption=caption)
            except telegram.error.TelegramError as e:
                logger.error(f"Ошибка при отправке изображения {image_path} в Telegram: {e}")
                raise
    except OSError as e:
        logger.error(f"Ошибка при открытии файла {image_path}: {e}")
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

    random.shuffle(existing_dirs)
    chosen_dir = random.choice(existing_dirs)

    try:
        files = os.listdir(chosen_dir)
    except OSError as e:
        raise ValueError(f"Ошибка при поиске изображений в {chosen_dir}: {e}")

    files = [
        f for f in files
        if os.path.isfile(os.path.join(chosen_dir, f)) and f.lower().endswith(valid_extensions)
    ]
    if not files:
        raise ValueError(f"В папке {chosen_dir} нет изображений с расширениями {valid_extensions}")
    return os.path.join(chosen_dir, random.choice(files))


def publish_image(bot):
    """Публикует случайное изображение в Telegram-канал с подписью.

    Args:
        bot (telegram.Bot): Объект Telegram-бота.
    """
    caption_templates = [
        "Космическое фото от @CosmoSnapsBot! Источник: {source} 🚀",
        "Погрузитесь в красоту космоса! 📸 Источник: {source}",
        "Новое изображение из космоса! 🌌 От @CosmoSnapsBot, источник: {source}",
        "Взгляните на эту космическую красоту! ✨ Источник: {source}",
        "Космос зовёт! @CosmoSnapsBot делится фото от {source} 🪐",
        "Из космоса с любовью! 💫 Источник: {source}",
        "Удивительное фото от @CosmoSnapsBot! Источник: {source} 🌠",
        "Путешествие по звёздам с @CosmoSnapsBot! Источник: {source} ⭐"
    ]

    image_dirs = ["nasa_images", "nasa_epic_photos", "spacex_images"]
    source = None
    try:
        image_path = get_random_image_from_random_folder(image_dirs)
        source = (
            "NASA APOD" if "nasa_images" in image_path else
            "NASA EPIC" if "nasa_epic_photos" in image_path else
            "SpaceX"
        )
        caption = random.choice(caption_templates).format(source=source)
        send_image_to_telegram(bot, image_path, caption)
    except ValueError as e:
        logger.error(f"Ошибка: {e}")
    except (OSError, telegram.error.TelegramError) as e:
        logger.error(f"Ошибка при публикации изображения: {e}")


def main():
    """Основная функция для запуска бота.

    Загружает переменные окружения, создаёт объект бота, настраивает расписание
    публикаций и запускает бесконечный цикл для выполнения задач.

    Raises:
        ValueError: Если отсутствуют необходимые переменные окружения или неверный формат интервала.
    """
    load_dotenv()
    token = os.getenv("TG_BOT_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")
    post_interval = os.getenv("TG_POST_INTERVAL_HOURS", "4")

    if not token:
        raise ValueError("TG_BOT_TOKEN not found in .env")
    if not chat_id:
        raise ValueError("TG_CHAT_ID not found in .env")

    try:
        post_interval = float(post_interval)
    except ValueError:
        raise ValueError("TG_POST_INTERVAL_HOURS must be a number")

    bot = telegram.Bot(token=token)

    print(bot.get_me())
    print(f"Текущая рабочая директория: {os.getcwd()}")
    print(f"Частота публикации: каждые {post_interval} часов")

    schedule.every(post_interval).hours.do(publish_image, bot=bot)

    publish_image(bot)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()