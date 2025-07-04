import os
import random
from dotenv import load_dotenv
import telegram


def send_image_to_telegram(bot, image_path: str, caption: str = None) -> None:
    """Отправляет изображение в Telegram-канал."""
    try:
        with open(image_path, "rb") as photo:
            bot.send_photo(chat_id=os.getenv("CHAT_ID"), photo=photo, caption=caption)
        print(f"Изображение отправлено: {image_path}")
    except Exception as e:
        print(f"Ошибка при отправке изображения {image_path}: {e}")


def get_random_image_from_random_folder(image_dirs: list) -> str:
    """Выбирает случайную папку и случайное изображение из неё."""
    valid_extensions = (".jpg", ".png")

    # Фильтруем существующие папки
    existing_dirs = [d for d in image_dirs if os.path.exists(d)]
    if not existing_dirs:
        raise ValueError("Ни одна из указанных папок не найдена")

    # Выбираем случайную папку
    chosen_dir = random.choice(existing_dirs)

    # Получаем список изображений в выбранной папке
    try:
        files = [
            f for f in os.listdir(chosen_dir)
            if os.path.isfile(os.path.join(chosen_dir, f)) and f.lower().endswith(valid_extensions)
        ]
        if not files:
            raise ValueError(f"В папке {chosen_dir} нет изображений с расширениями {valid_extensions}")
        # Выбираем случайное изображение
        return os.path.join(chosen_dir, random.choice(files))
    except Exception as e:
        raise ValueError(f"Ошибка при поиске изображений в {chosen_dir}: {e}")


def main():
    # Загружаем переменные из .env
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")

    # Проверяем, что токен и chat_id загружены
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not found in .env")
    if not chat_id:
        raise ValueError("CHAT_ID not found in .env")

    # Создаём объект бота
    bot = telegram.Bot(token=token)

    # Проверяем, что бот работает
    print(bot.get_me())

    # Выводим текущую рабочую директорию для отладки
    print(f"Текущая рабочая директория: {os.getcwd()}")

    # Список папок с изображениями
    image_dirs = ["nasa_images", "nasa_epic_photos", "spacex_images"]
    caption = "Космическое фото от @CosmoSnapsBot! 🚀"

    try:
        # Получаем случайное изображение из случайной папки
        image_path = get_random_image_from_random_folder(image_dirs)
        # Отправляем изображение
        send_image_to_telegram(bot, image_path, caption)
    except ValueError as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()