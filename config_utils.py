import os
from dotenv import load_dotenv

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

def restrict_count(count: int, max_count: int, api_name: str) -> None:
    """Проверяет, что количество изображений не превышает максимум.

    Args:
        count (int): Запрошенное количество изображений.
        max_count (int): Максимальное допустимое количество.
        api_name (str): Название API для сообщения об ошибке.

    Raises:
        ValueError: Если count превышает max_count.
    """
    if count > max_count:
        raise ValueError(f"Максимальное количество изображений для {api_name}: {max_count}")