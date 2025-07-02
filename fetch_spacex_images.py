import requests
from utils import run_script, logger
from common import download_image

def fetch_spacex_last_launch(launch_id: str = None, save_dir: str = "spacex_images") -> None:
    """Получает фотографии запуска SpaceX по ID или последнего запуска и сохраняет их локально.

    Args:
        launch_id (str, optional): Идентификатор запуска SpaceX в формате API v4. Если None, загружается последний запуск.
        save_dir (str, optional): Папка для сохранения изображений. По умолчанию 'spacex_images'.

    Raises:
        requests.exceptions.HTTPError: Ошибки при выполнении HTTP-запроса.
        requests.exceptions.RequestException: Другие ошибки запроса.
    """
    if launch_id:
        url = f"https://api.spacexdata.com/v4/launches/{launch_id}"
        prefix = f"spacex_{launch_id}"
    else:
        url = "https://api.spacexdata.com/v4/launches/latest"
        prefix = "spacex_latest"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        image_urls = data.get("links", {}).get("flickr", {}).get("original", [])

        if not image_urls:
            logger.warning(f"Фотографий для запуска {'последнего' if not launch_id else launch_id} не найдено.")
            return

        logger.info(f"Найдено фотографий: {len(image_urls)}")
        for i, link in enumerate(image_urls):
            try:
                download_image(link, save_dir, i, prefix=prefix)
            except Exception as e:
                logger.error(f"Ошибка при загрузке {link}: {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при выполнении запроса к SpaceX API: {e}")
        raise

if __name__ == "__main__":
    run_script(
        description="Скачивание изображений запуска SpaceX",
        main_func=fetch_spacex_last_launch,
        default_args={
            "launch_id": {"type": str, "default": None, "help": "ID запуска SpaceX (по умолчанию загружается последний запуск)"},
            "save_dir": {"type": str, "default": "spacex_images", "help": "Папка для сохранения изображений (по умолчанию spacex_images)"}
        },
        api_key_required=False
    )