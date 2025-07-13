import argparse
from dotenv import load_dotenv
import os
import requests
from utils import logger
from image_utils import download_image, get_api_key

def main(api_key: str, save_dir: str = "nasa_images", count: int = 30, max_images: int = 100) -> None:
    """Получает и сохраняет фотографии дня NASA APOD.

    Args:
        api_key (str): API-ключ для доступа к NASA API.
        save_dir (str, optional): Папка для сохранения изображений. По умолчанию 'nasa_images'.
        count (int, optional): Количество изображений для загрузки (максимум 100). По умолчанию 30.
        max_images (int, optional): Максимальное количество изображений для загрузки. По умолчанию 100.

    Raises:
        requests.exceptions.HTTPError: Ошибки при выполнении HTTP-запроса.
        requests.exceptions.RequestException: Другие ошибки запроса.
        ValueError: Если count превышает допустимое значение.
    """
    if count > max_images:
        raise ValueError(f"Максимальное количество изображений для загрузки: 100")

    params = {
        "api_key": api_key,
        "count": count,
        "thumbs": True
    }
    url = "https://api.nasa.gov/planetary/apod"

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    apod_records = response.json()

    image_index = 0
    for _, apod_entry in enumerate(apod_records):
        if apod_entry.get("media_type") == "image" and apod_entry.get("url"):
            try:
                download_image(apod_entry["url"], save_dir, image_index, prefix="nasa_apod", params=None)
                image_index += 1
            except (ValueError, requests.exceptions.RequestException, OSError) as e:
                logger.error(f"Ошибка при загрузке {apod_entry.get('url', 'без URL')}: {e}")
        else:
            logger.warning(f"Пропущено (не изображение или нет URL): {apod_entry.get('title', 'без названия')}")

if __name__ == "__main__":
    MAX_APOD_IMAGES = 100  # Максимальное количество изображений для загрузки через NASA APOD API
    parser = argparse.ArgumentParser(description="Загрузка изображений NASA APOD")
    parser.add_argument(
        "--count",
        type=int,
        default=30,
        help="Сколько изображений скачать (по умолчанию 30, максимум 100)"
    )
    parser.add_argument(
        "--save_dir",
        type=str,
        default="nasa_images",
        help="Папка для сохранения изображений (по умолчанию nasa_images)"
    )
    parser.add_argument(
        "--api_key",
        type=str,
        help="API-ключ (если не указан — берётся из .env)"
    )
    args = parser.parse_args()

    try:
        api_key = get_api_key("NASA_API_KEY", args.api_key)
        main(api_key=api_key, count=args.count, save_dir=args.save_dir, max_images=MAX_APOD_IMAGES)
    except (ValueError, requests.exceptions.RequestException) as e:
        logger.error(f"Ошибка: {e}")
        raise