import requests
from datetime import datetime
from urllib.parse import urlencode
from utils import run_script, logger
from common import download_image


def download_epic_images(count: int = 10, save_dir: str = "epic_images", api_key: str = None) -> None:
    """Скачивает изображения Земли через NASA EPIC API.

    Args:
        count (int, optional): Количество изображений для загрузки (максимум 10). По умолчанию 10.
        save_dir (str, optional): Папка для сохранения изображений. По умолчанию 'epic_images'.
        api_key (str): API-ключ для доступа к NASA API.

    Raises:
        ValueError: Если count превышает допустимое значение.
        requests.exceptions.RequestException: Ошибки при выполнении HTTP-запроса.
    """
    if count > 10:
        raise ValueError("Максимальное количество изображений для загрузки: 10")

    params = {"api_key": api_key}
    metadata_url = f"https://api.nasa.gov/EPIC/api/natural/images?{urlencode(params)}"

    try:
        response = requests.get(metadata_url, timeout=30)
        response.raise_for_status()
        images_data = response.json()[:count]

        for i, img in enumerate(images_data):
            try:
                img_date = datetime.strptime(img["date"], "%Y-%m-%d %H:%M:%S")
                date_path = img_date.strftime("%Y/%m/%d")
                image_url = (
                    f"https://api.nasa.gov/EPIC/archive/natural/"
                    f"{date_path}/png/{img['image']}.png?"
                    f"{urlencode({'api_key': api_key})}"
                )
                download_image(image_url, save_dir, i, prefix="nasa_epic")
            except ValueError as e:
                logger.error(f"Ошибка формата даты для изображения {img.get('image', 'без имени')}: {e}")
            except Exception as e:
                logger.error(f"Ошибка при загрузке изображения {img.get('image', 'без имени')}: {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при выполнении запроса к NASA EPIC API: {e}")
        raise


if __name__ == "__main__":
    run_script(
        description="Скачивание изображений Земли с NASA EPIC API",
        main_func=download_epic_images,
        default_args={
            "count": {"type": int, "default": 10, "help": "Сколько изображений скачать (по умолчанию 10, максимум 10)"},
            "save_dir": {"type": str, "default": "nasa_epic_photos",
                         "help": "Папка для сохранения изображений (по умолчанию nasa_epic_photos)"}
        },
        api_key_required=True
    )
