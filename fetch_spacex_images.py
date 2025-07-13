import argparse
import requests
from utils import logger
from image_utils import download_image

def get_patch_urls(launch_info: dict) -> list:
    """Извлекает URL патчей из данных запуска SpaceX.

    Args:
        launch_info (dict): Данные запуска от SpaceX API.

    Returns:
        list: Список URL патчей (small и/или large).
    """
    patch_urls = []
    patch_urls_dict = launch_info.get("links", {}).get("patch", {})
    if patch_urls_dict.get("small"):
        patch_urls.append(patch_urls_dict["small"])
    if patch_urls_dict.get("large"):
        patch_urls.append(patch_urls_dict["large"])
    return patch_urls

def get_image_urls(launch_info: dict, launch_id: str = None) -> tuple[list, str]:
    """Извлекает URL изображений (Flickr или патчи) и префикс для имен файлов.

    Args:
        launch_info (dict): Данные запуска от SpaceX API.
        launch_id (str, optional): ID запуска для формирования префикса.

    Returns:
        tuple[list, str]: Список URL изображений и префикс для имен файлов.
    """
    prefix = f"spacex_{launch_id}" if launch_id else "spacex_latest"
    image_urls = launch_info.get("links", {}).get("flickr", {}).get("original", [])
    if image_urls:
        logger.info(f"Найдено изображений {'запуска ' + launch_id if launch_id else 'последнего запуска'}: {len(image_urls)}")
        return image_urls, prefix

    image_urls = get_patch_urls(launch_info)
    if image_urls:
        logger.info(f"Используются патчи {'запуска ' + launch_id if launch_id else 'последнего запуска'}: {len(image_urls)}")
    return image_urls, prefix

def main(launch_id: str = None, save_dir: str = "spacex_images",
         url: str = "https://api.spacexdata.com/v4/launches/latest",
         prefix: str = "spacex_latest") -> None:
    """Получает фотографии запуска SpaceX по ID или последнего запуска и сохраняет их локально.

    Args:
        launch_id (str, optional): Идентификатор запуска SpaceX в формате API v4.
            Если None, загружается последний запуск.
        save_dir (str, optional): Папка для сохранения изображений. По умолчанию 'spacex_images'.
        url (str, optional): URL для запроса к SpaceX API. По умолчанию для последнего запуска.
        prefix (str, optional): Префикс для имен файлов. По умолчанию 'spacex_latest'.

    Raises:
        requests.exceptions.HTTPError: Ошибки при выполнения HTTP-запроса.
        requests.exceptions.RequestException: Другие ошибки запроса.
    """
    if launch_id:
        url = f"https://api.spacexdata.com/v4/launches/{launch_id}"
        prefix = f"spacex_{launch_id}"

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    launch_info = response.json()
    logger.debug(f"Полный ответ API: {launch_info}")
    image_urls, prefix = get_image_urls(launch_info, launch_id)

    if not image_urls:
        fallback_launch_id = "5eb87d47ffd86e000604b38a"
        fallback_url = f"https://api.spacexdata.com/v4/launches/{fallback_launch_id}"
        try:
            fallback_response = requests.get(fallback_url, timeout=30)
            fallback_response.raise_for_status()
            fallback_launch_info = fallback_response.json()
            logger.debug(f"Полный ответ API для запасного запуска: {fallback_launch_info}")
            image_urls, prefix = get_image_urls(fallback_launch_info, fallback_launch_id)
            if not image_urls:
                logger.warning(f"Фотографий и патчей для последнего и запасного запуска не найдено.")
                return
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при выполнении запроса к запасному запуску SpaceX API: {e}")
            return

    for i, image_url in enumerate(image_urls):
        try:
            download_image(image_url, save_dir, i, prefix=prefix, params=None)
        except (ValueError, requests.exceptions.RequestException, OSError) as e:
            logger.error(f"Ошибка при загрузке {image_url}: {e}")

if __name__ == "__main__":
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

    try:
        main(launch_id=args.launch_id, save_dir=args.save_dir)
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка: {e}")
        raise