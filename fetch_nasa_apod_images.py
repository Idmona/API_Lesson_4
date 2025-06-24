import os
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv


def download_image(url: str, save_dir: str, index: int) -> None:
    """Загружает изображение по URL и сохраняет его в указанную папку с именем nasa_apod_N.ext.

    Args:
        url (str): URL изображения.
        save_dir (str): Путь к директории для сохранения изображения.
        index (int): Номер, который будет использоваться для имени файла.

    Raises:
        requests.exceptions.RequestException: Ошибки при выполнении HTTP-запроса.
        OSError: Ошибки при создании папки или записи файла.
    """
    os.makedirs(save_dir, exist_ok=True)

    # Получаем расширение файла
    parsed_url = urlparse(url)
    ext = os.path.splitext(parsed_url.path)[1] or ".jpg"  # Если нет расширения — используем .jpg

    # Формируем имя файла: nasa_apod_0.jpg, nasa_apod_1.jpg и т.д.
    filename = f"nasa_apod_{index}{ext}"
    save_path = os.path.join(save_dir, filename)

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    with open(save_path, "wb") as file:
        file.write(response.content)
    print(f"Сохранено: {save_path}")


def fetch_nasa_apod(api_key: str, save_dir: str = "nasa_images", count: int = 30) -> None:
    """Получает и сохраняет фотографии дня NASA APOD.

    Args:
        api_key (str): API-ключ для доступа к NASA API.
        save_dir (str, optional): Папка для сохранения изображений. По умолчанию "nasa_images".
        count (int, optional): Количество изображений для загрузки. По умолчанию 30.

    Raises:
        requests.exceptions.HTTPError: Ошибки при выполнении HTTP-запроса.
        requests.exceptions.RequestException: Другие ошибки запроса.
    """
    params = {
        "api_key": api_key,
        "count": count,
        "thumbs": True
    }
    url = "https://api.nasa.gov/planetary/apod"

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    apod_data = response.json()

    image_index = 0

    for item in apod_data:
        if item.get("media_type") == "image" and item.get("url"):
            try:
                download_image(item["url"], save_dir, image_index)
                image_index += 1
            except Exception as e:
                print(f"Ошибка при загрузке {item['url']}: {e}")
        else:
            print(f"Пропущено (не изображение или нет URL): {item.get('title', 'без названия')}")


def main():
    load_dotenv()
    NASA_API_KEY = os.getenv("NASA_API_KEY")

    if not NASA_API_KEY:
        raise ValueError("API-ключ NASA не найден. Убедитесь, что он указан в .env как NASA_API_KEY.")

    fetch_nasa_apod(NASA_API_KEY, count=30)


if __name__ == "__main__":
    main()
