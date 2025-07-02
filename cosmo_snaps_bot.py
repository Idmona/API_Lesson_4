import os
from dotenv import load_dotenv
import telegram

# Загружаем переменные из .env
load_dotenv()
token = os.getenv("TELEGRAM_BOT_TOKEN")

# Проверяем, что токен загружен
if not token:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in .env")

# Создаём объект бота
bot = telegram.Bot(token=token)

# Проверяем, что бот работает
print(bot.get_me())

# Отправляем сообщение в группу
chat_id = "-1002722619275"  # ID твоей группы
message = "Привет, это @CosmoSnapsBot! Я готов отправлять космические изображения!"
bot.send_message(chat_id=chat_id, text=message)
