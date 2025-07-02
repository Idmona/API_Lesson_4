from dotenv import load_dotenv
import os
import requests
from urllib.parse import urlparse
from utils import logger

def download_image(url: str, save_dir: str, index: int, prefix: str = "image") -> None:
    """Загружает изображение по URL и сохраняет его в указанную папку с именем {prefix}_{index}.ext.

    Args:
        url (str): URL изображения.
        save_dir (str): Путь к директории для сохранения изображения.
        index (int): Номер для имени файла.
        prefix (str, optional): Префикс имени файла (по умолчанию 'image').

    Raises:
        requests.exceptions.RequestException: Ошибки при выполнении HTTP-запроса.
        OSError: Ошибки при создании папки или записи файла.
        ValueError: Если URL некорректен.
    """

    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        raise ValueError(f"Некорректный URL: {url}")

    os.makedirs(save_dir, exist_ok=True)
    ext = os.path.splitext(parsed_url.path)[1] or ".jpg"
    save_path = os.path.join(save_dir, f"{prefix}_{index}{ext}")

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(save_path, "wb") as file:
            file.write(response.content)
        logger.info(f"Скачано: {save_path}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при загрузке {url}: {e}")
        raise

def get_api_key(env_var_name: str, cli_arg_value: str = None) -> str:
    """Получает API-ключ из аргументов командной строки или переменной окружения.

    Args:
        env_var_name (str): Имя переменной окружения.
        cli_arg_value (str, optional): Значение API-ключа из аргументов командной строки.

    Returns:
        str: API-ключ.

    Raises:
        ValueError: Если API-ключ не найден.
    """

    load_dotenv()
    api_key = cli_arg_value or os.getenv(env_var_name)
    if not api_key:
        raise ValueError(f"API-ключ {env_var_name} не найден. Укажите его через --api_key или в .env.")
    return api_key