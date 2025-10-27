import argparse
import os
import requests
from utils import logger
from image_utils import download_image
from config_utils import get_api_key

MAX_EPIC_IMAGES = 10

def download_nasa_epic_images(nasa_api_key: str = None, save_dir: str = "nasa_epic_photos") -> None:
    """Загружает изображения NASA EPIC и сохраняет их локально.

    Args:
        nasa_api_key (str, optional): Ключ API NASA. По умолчанию None.
        save_dir (str, optional): Папка для сохранения. По умолчанию 'nasa_epic_photos'.

    Raises:
        ValueError: Если ключ API отсутствует.
        requests.exceptions.RequestException: При ошибках запроса к API.
    """
    nasa_api_key = get_api_key("NASA_API_KEY", nasa_api_key)

    url = "https://api.nasa.gov/EPIC/api/natural"
    params = {"api_key": nasa_api_key}

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        images_data = response.json()
        logger.debug(f"Полный ответ API: {images_data}")

        if len(images_data) > MAX_EPIC_IMAGES:
            images_data = images_data[:MAX_EPIC_IMAGES]
            logger.info(f"Ограничено до {MAX_EPIC_IMAGES} изображений")

        for index, image_data in enumerate(images_data):
            image_id = image_data.get("image")
            date = image_data.get("date").split(" ")[0].replace("-", "/")
            if not image_id or not date:
                logger.warning(f"Пропущен объект {index}: отсутствует ID или дата")
                continue
            image_url = f"https://api.nasa.gov/EPIC/archive/natural/{date}/png/{image_id}.png"
            try:
                download_image(image_url, save_dir, index, prefix="nasa_epic", params={"api_key": nasa_api_key})
            except (ValueError, requests.exceptions.RequestException, OSError) as e:
                logger.error(f"Ошибка при загрузке {image_url}: {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при выполнении запроса к NASA EPIC API: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Скачивание изображений NASA EPIC")
    parser.add_argument(
        "--nasa_api_key",
        type=str,
        default=os.getenv("NASA_API_KEY"),
        help="NASA API key (default: from NASA_API_KEY env variable)"
    )
    parser.add_argument(
        "--save_dir",
        type=str,
        default="nasa_epic_photos",
        help="Directory to save images (default: nasa_epic_photos)"
    )
    args = parser.parse_args()
    download_nasa_epic_images(args.nasa_api_key, args.save_dir)

if __name__ == "__main__":
    main()