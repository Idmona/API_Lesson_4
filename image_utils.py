import os
import requests
from urllib.parse import urlparse
from utils import logger

def restrict_url(url: str) -> None:
    """Проверяет корректность URL изображения.

    Args:
        url (str): URL изображения.

    Raises:
        ValueError: Если URL пустой или некорректный.
    """
    if not url:
        raise ValueError("URL изображения пустой")

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Некорректная схема URL: {parsed.scheme}")
    if not parsed.netloc:
        raise ValueError("URL не содержит доменного имени")
    if not parsed.path:
        raise ValueError("URL не содержит пути к изображению")

def download_image(url: str, save_dir: str, index: int, prefix: str = "", params: dict = None) -> None:
    """Скачивает изображение по URL и сохраняет его в указанную папку.

    Args:
        url (str): URL изображения.
        save_dir (str): Папка для сохранения.
        index (int): Индекс для имени файла.
        prefix (str, optional): Префикс для имени файла.
        params (dict, optional): GET-параметры для запроса.

    Raises:
        ValueError: Если URL пустой или некорректный.
        requests.exceptions.RequestException: Ошибки при загрузке.
        OSError: Ошибки при сохранении файла.
    """
    restrict_url(url)

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    os.makedirs(save_dir, exist_ok=True)
    extension = os.path.splitext(urlparse(url).path)[1] or ".jpg"
    filename = f"{prefix}_{index:03d}{extension}" if prefix else f"image_{index:03d}{extension}"
    filepath = os.path.join(save_dir, filename)

    with open(filepath, "wb") as f:
        f.write(response.content)

    logger.info(f"Изображение сохранено: {filepath}")