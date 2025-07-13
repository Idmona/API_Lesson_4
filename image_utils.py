import os
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv
from utils import logger


def download_image(url: str, save_dir: str, index: int, prefix: str = "", params: dict = None) -> None:
    """Скачивает изображение по URL и сохраняет его в указанную папку.

    Args:
        url (str): URL изображения.
        save_dir (str): Папка для сохранения.
        index (int): Индекс для имени файла.
        prefix (str, optional): Префикс для имени файла.
        params (dict, optional): GET-параметры для запроса.

    Raises:
        ValueError: Если URL пустой или недоступен.
        requests.exceptions.RequestException: Ошибки при загрузке.
        OSError: Ошибки при сохранении файла.
    """
    if not url:
        raise ValueError("URL изображения пустой")

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    os.makedirs(save_dir, exist_ok=True)
    extension = os.path.splitext(urlparse(url).path)[1] or ".jpg"
    filename = f"{prefix}_{index:03d}{extension}" if prefix else f"image_{index:03d}{extension}"
    filepath = os.path.join(save_dir, filename)

    with open(filepath, "wb") as f:
        f.write(response.content)
    logger.info(f"Изображение сохранено: {filepath}")


def get_api_key(env_key: str, cli_key: str = None) -> str:
    """Получает API-ключ из аргументов командной строки или .env файла.

    Args:
        env_key (str): Название переменной окружения для ключа.
        cli_key (str, optional): Ключ из аргументов командной строки.

    Returns:
        str: API-ключ.

    Raises:
        ValueError: Если ключ не найден.
    """
    load_dotenv()
    api_key = cli_key or os.getenv(env_key)
    if not api_key:
        raise ValueError(f"API-ключ {env_key} не найден")
    return api_key