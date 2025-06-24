import os

import requests
from dotenv import load_dotenv


def download_image(url: str, save_path: str) -> None:
    """Загружает изображение по URL и сохраняет его по указанному пути.
    Args:
        url (str): URL-адрес изображения для скачивания.
        save_path (str): Полный путь для сохранения файла, включая имя файла и расширение.

    Raises:
        requests.exceptions.HTTPError: Возникает, если HTTP-запрос завершился с ошибкой.
        requests.exceptions.RequestException: Возникает при других ошибках во время запроса.
        OSError: Возникает при ошибках создания директорий или записи файла.
    """

    folder = os.path.dirname(save_path)
    if folder:
        os.makedirs(folder, exist_ok=True)

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    with open(save_path, "wb") as file:
        file.write(response.content)


def fetch_spacex_last_launch(launch_id: str, api_key: str = None):
    """Получает фотографии последнего запуска SpaceX по ID запуска и сохраняет их локально.

        Args:
            launch_id (str): Идентификатор запуска SpaceX в формате API v4.
            api_key (str, необязательный): API-ключ для авторизации, если требуется.

        Raises:
            requests.exceptions.HTTPError: Возникает, если HTTP-запрос завершился с ошибкой.
            requests.exceptions.RequestException: Возникает при других ошибках во время запроса.
            OSError: Возникает при ошибках создания директорий или записи файла.
        """
    url = f"https://api.spacexdata.com/v4/launches/{launch_id}"

    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    data = response.json()
    image_urls = data.get("links", {}).get("flickr", {}).get("original", [])

    if not image_urls:
        print("Фотографий для этого запуска не найдено.")
        return

    print("Найдено фото:", len(image_urls))
    image_folder = "spacex_images"
    os.makedirs(image_folder, exist_ok=True)
    for i, link in enumerate(image_urls, start=0):
        ext = os.path.splitext(link)[1]
        filename = os.path.join(image_folder, f"spacex_{i}{ext}")
        download_image(link, filename)


def main():
    load_dotenv()

    SPACEX_API_KEY = os.getenv("SPACEX_API_KEY")

    launch_id = "5eb87d47ffd86e000604b38a"
    fetch_spacex_last_launch(launch_id, api_key=SPACEX_API_KEY)


if __name__ == "__main__":
    main()
