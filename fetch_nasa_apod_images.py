import argparse
import os
from datetime import datetime, timedelta
import requests
from utils import logger
from image_utils import download_image
from config_utils import get_api_key, restrict_count

MAX_APOD_IMAGES = 100

def download_nasa_apod_images(nasa_api_key: str = None, count: int = 5, save_dir: str = "nasa_images") -> None:
    """Загружает изображения NASA APOD и сохраняет их локально.

    Args:
        nasa_api_key (str, optional): Ключ API NASA. По умолчанию None.
        count (int, optional): Количество изображений для загрузки. По умолчанию 5.
        save_dir (str, optional): Папка для сохранения. По умолчанию 'nasa_images'.

    Raises:
        ValueError: Если ключ API отсутствует или count превышает максимум.
        requests.exceptions.RequestException: При ошибках запроса к API.
    """
    nasa_api_key = get_api_key("NASA_API_KEY", nasa_api_key)
    restrict_count(count, MAX_APOD_IMAGES, "NASA APOD")

    url = "https://api.nasa.gov/planetary/apod"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=count - 1)
    params = {
        "api_key": nasa_api_key,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        images_data = response.json()
        logger.debug(f"Полный ответ API: {images_data}")

        for index, image_data in enumerate(images_data):
            if image_data.get("media_type") != "image":
                logger.warning(f"Пропущен объект {index}: не является изображением")
                continue
            image_url = image_data.get("url")
            if not image_url:
                logger.warning(f"Пропущен объект {index}: отсутствует URL изображения")
                continue
            try:
                download_image(image_url, save_dir, index, prefix="nasa_apod", params=None)
            except (ValueError, requests.exceptions.RequestException, OSError) as e:
                logger.error(f"Ошибка при загрузке {image_url}: {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при выполнении запроса к NASA APOD API: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Скачивание изображений NASA APOD")
    parser.add_argument(
        "--nasa_api_key",
        type=str,
        default=os.getenv("NASA_API_KEY"),
        help="NASA API key (default: from NASA_API_KEY env variable)"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help=f"Number of images to download (default: 5, max: {MAX_APOD_IMAGES})"
    )
    parser.add_argument(
        "--save_dir",
        type=str,
        default="nasa_images",
        help="Directory to save images (default: nasa_images)"
    )
    args = parser.parse_args()
    download_nasa_apod_images(args.nasa_api_key, args.count, args.save_dir)

if __name__ == "__main__":
    main()