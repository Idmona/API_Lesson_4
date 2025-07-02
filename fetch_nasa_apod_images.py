import requests
from utils import run_script, logger
from common import download_image

def fetch_nasa_apod(api_key: str, save_dir: str = "nasa_images", count: int = 30) -> None:
    """Получает и сохраняет фотографии дня NASA APOD.

    Args:
        api_key (str): API-ключ для доступа к NASA API.
        save_dir (str, optional): Папка для сохранения изображений. По умолчанию 'nasa_images'.
        count (int, optional): Количество изображений для загрузки (максимум 100). По умолчанию 30.

    Raises:
        requests.exceptions.HTTPError: Ошибки при выполнении HTTP-запроса.
        requests.exceptions.RequestException: Другие ошибки запроса.
        ValueError: Если count превышает допустимое значение.
    """
    if count > 100:
        raise ValueError("Максимальное количество изображений для загрузки: 100")

    params = {
        "api_key": api_key,
        "count": count,
        "thumbs": True
    }
    url = "https://api.nasa.gov/planetary/apod"

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        apod_data = response.json()

        image_index = 0
        for item in apod_data:
            if item.get("media_type") == "image" and item.get("url"):
                try:
                    download_image(item["url"], save_dir, image_index, prefix="nasa_apod")
                    image_index += 1
                except Exception as e:
                    logger.error(f"Ошибка при загрузке {item.get('url', 'без URL')}: {e}")
            else:
                logger.warning(f"Пропущено (не изображение или нет URL): {item.get('title', 'без названия')}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при выполнении запроса к NASA API: {e}")
        raise

if __name__ == "__main__":
    run_script(
        description="Загрузка изображений NASA APOD",
        main_func=fetch_nasa_apod,
        default_args={
            "count": {"type": int, "default": 30, "help": "Сколько изображений скачать (по умолчанию 30, максимум 100)"},
            "save_dir": {"type": str, "default": "nasa_images", "help": "Папка для сохранения изображений (по умолчанию nasa_images)"}
        },
        api_key_required=True
    )