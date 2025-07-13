import argparse
from datetime import datetime
from urllib.parse import urlencode
from dotenv import load_dotenv
import os
import requests
from utils import logger
from image_utils import download_image, get_api_key

def main(count: int = 10, save_dir: str = "epic_images", api_key: str = None, max_images: int = 10) -> None:
    """Скачивает изображения Земли через NASA EPIC API.

    Args:
        count (int, optional): Количество изображений для загрузки (максимум 10). По умолчанию 10.
        save_dir (str, optional): Папка для сохранения изображений. По умолчанию 'epic_images'.
        api_key (str): API-ключ для доступа к NASA API.
        max_images (int, optional): Максимальное количество изображений для загрузки. По умолчанию 10.

    Raises:
        ValueError: Если count превышает допустимое значение.
        requests.exceptions.RequestException: Ошибки при выполнении HTTP-запроса.
    """
    if count > max_images:
        raise ValueError(f"Максимальное количество изображений для загрузки: 10")

    params = {"api_key": api_key}
    epic_api_url = "https://api.nasa.gov/EPIC/api/natural/images"
    response = requests.get(epic_api_url, params=params, timeout=30)
    response.raise_for_status()
    epic_records = response.json()[:count]

    for i, epic_record in enumerate(epic_records):
        try:
            img_date = datetime.strptime(epic_record["date"], "%Y-%m-%d %H:%M:%S")
            date_path = img_date.strftime("%Y/%m/%d")
            image_url = (
                f"https://api.nasa.gov/EPIC/archive/natural/"
                f"{date_path}/png/{epic_record['image']}.png"
            )
            download_image(image_url, save_dir, i, prefix="nasa_epic", params={"api_key": api_key})
        except ValueError as e:
            logger.error(f"Ошибка формата даты для изображения {epic_record.get('image', 'без имени')}: {e}")
        except (requests.exceptions.RequestException, OSError) as e:
            logger.error(f"Ошибка при загрузке изображения {epic_record.get('image', 'без имени')}: {e}")

if __name__ == "__main__":
    MAX_EPIC_IMAGES = 10  # Максимальное количество изображений для загрузки через NASA EPIC API
    parser = argparse.ArgumentParser(description="Скачивание изображений Земли с NASA EPIC API")
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Сколько изображений скачать (по умолчанию 10, максимум 10)"
    )
    parser.add_argument(
        "--save_dir",
        type=str,
        default="nasa_epic_photos",
        help="Папка для сохранения изображений (по умолчанию nasa_epic_photos)"
    )
    parser.add_argument(
        "--api_key",
        type=str,
        help="API-ключ (если не указан — берётся из .env)"
    )
    args = parser.parse_args()

    try:
        api_key = get_api_key("NASA_API_KEY", args.api_key)
        main(count=args.count, save_dir=args.save_dir, api_key=api_key, max_images=MAX_EPIC_IMAGES)
    except (ValueError, requests.exceptions.RequestException) as e:
        logger.error(f"Ошибка: {e}")
        raise