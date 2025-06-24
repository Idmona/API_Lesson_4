import os
from datetime import datetime
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv


def download_epic_images(count: int = 10, save_dir: str = "epic_images"):
    """
    Скачивает указанное количество изображений Земли через NASA EPIC API.

    Args:
        count (int, optional): Количество изображений для загрузки. По умолчанию 10.
        save_dir (str, optional): Папка для сохранения изображений. По умолчанию 'epic_images'.

    Raises:
        ValueError: Если не найден NASA_API_KEY в переменных окружения.
        requests.exceptions.RequestException: Ошибки при выполнении HTTP-запроса.
        OSError: Ошибки при создании папки или записи файла.
    """

    api_key = os.getenv("NASA_API_KEY")
    if not api_key:
        raise ValueError("NASA_API_KEY не найден в переменных окружения")

    os.makedirs(save_dir, exist_ok=True)

    params = {"api_key": api_key}
    metadata_url = f"https://api.nasa.gov/EPIC/api/natural/images?{urlencode(params)}"

    try:
        response = requests.get(metadata_url)
        response.raise_for_status()
        images_data = response.json()[:count]

        for img in images_data:
            img_date = datetime.strptime(img['date'], "%Y-%m-%d %H:%M:%S")
            date_path = img_date.strftime("%Y/%m/%d")

            image_url = (
                f"https://api.nasa.gov/EPIC/archive/natural/"
                f"{date_path}/png/{img['image']}.png?"
                f"{urlencode({'api_key': api_key})}"
            )

            img_data = requests.get(image_url)
            img_data.raise_for_status()

            save_path = os.path.join(save_dir, f"{img['image']}.png")
            with open(save_path, "wb") as f:
                f.write(img_data.content)

            print(f"Скачано: {save_path}")

    except Exception as e:
        print(f"Ошибка: {e}")


def main():
    load_dotenv()

    DOWNLOAD_COUNT = 10
    SAVE_DIRECTORY = "nasa_epic_photos"

    download_epic_images(
        count=DOWNLOAD_COUNT,
        save_dir=SAVE_DIRECTORY
    )


if __name__ == "__main__":
    main()
