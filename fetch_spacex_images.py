import argparse
import requests
from utils import logger
from image_utils import download_image

def get_patch_urls(launch_data: dict) -> list:
    """Извлекает URL патчей из данных запуска SpaceX.
    Args:
        launch_data (dict): Данные запуска от SpaceX API.
    Returns:
        list: Список URL патчей (small и/или large).
    """
    patch = launch_data.get("links", {}).get("patch", {})
    patch_urls = []
    if patch.get("small"):
        patch_urls.append(patch["small"])
    if patch.get("large"):
        patch_urls.append(patch["large"])
    return patch_urls

def get_spacex_prefix(launch_id: str = None) -> str:
    """Возвращает префикс для имен файлов на основе ID запуска.
    Args:
        launch_id (str, optional): ID запуска SpaceX.
    Returns:
        str: Префикс для имен файлов.
    """
    return f"spacex_{launch_id}" if launch_id else "spacex_latest"

def extract_image_urls_and_prefix(launch_data: dict, launch_id: str = None) -> tuple[list, str]:
    """Извлекает URL изображений (Flickr или патчи) и префикс для имен файлов.
    Args:
        launch_data (dict): Данные запуска от SpaceX API.
        launch_id (str, optional): ID запуска для формирования префикса.
    Returns:
        tuple[list, str]: Список URL изображений и префикс для имен файлов.
    """
    prefix = get_spacex_prefix(launch_id)
    image_urls = launch_data.get("links", {}).get("flickr", {}).get("original", [])
    launch_name = f"запуска {launch_id}" if launch_id else "последнего запуска"
    if image_urls:
        logger.info(f"Найдено изображений {launch_name}: {len(image_urls)}")
        return image_urls, prefix

    image_urls = get_patch_urls(launch_data)
    if image_urls:
        logger.info(f"Используются патчи {launch_name}: {len(image_urls)}")
        return image_urls, prefix
    return [], prefix

def fetch_launch_data(launch_id: str = None) -> dict:
    """Получает данные запуска от SpaceX API.
    Args:
        launch_id (str, optional): ID запуска. Если None, запрашивается последний запуск.
    Returns:
        dict: Данные запуска.
    Raises:
        requests.exceptions.RequestException: При ошибках запроса.
    """
    url = f"https://api.spacexdata.com/v4/launches/{launch_id}" if launch_id else "https://api.spacexdata.com/v4/launches/latest"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    launch_data = response.json()
    logger.debug(f"Полный ответ API: {launch_data}")
    return launch_data

def download_spacex_images(launch_id: str = "5eb87d47ffd86e000604b38a", save_dir: str = "spacex_images") -> None:
    """Загружает изображения запуска SpaceX и сохраняет их локально.
    Args:
        launch_id (str, optional): ID запуска SpaceX. По умолчанию запасной ID.
        save_dir (str, optional): Папка для сохранения. По умолчанию 'spacex_images'.
    Raises:
        requests.exceptions.RequestException: При ошибках запроса к API.
    """
    try:
        launch_data = fetch_launch_data(launch_id)
        image_urls, prefix = extract_image_urls_and_prefix(launch_data, launch_id)
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при загрузке данных запуска {launch_id or 'последнего'}: {e}")
        return

    if not image_urls:
        logger.warning(f"Фотографий и патчей для запуска {launch_id or 'последнего'} не найдено.")
        return

    for index, image_url in enumerate(image_urls):
        try:
            download_image(image_url, save_dir, index, prefix=prefix, params=None)
        except (ValueError, requests.exceptions.RequestException, OSError) as e:
            logger.error(f"Ошибка при загрузке {image_url}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Скачивание изображений запуска SpaceX")
    parser.add_argument(
        "--launch_id",
        type=str,
        default=None,
        help="ID запуска SpaceX (по умолчанию загружается последний запуск)"
    )
    parser.add_argument(
        "--save_dir",
        type=str,
        default="spacex_images",
        help="Папка для сохранения изображений (по умолчанию spacex_images)"
    )
    args = parser.parse_args()
    download_spacex_images(launch_id=args.launch_id, save_dir=args.save_dir)

if __name__ == "__main__":
    main()