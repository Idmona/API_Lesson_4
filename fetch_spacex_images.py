import requests
from utils import run_script, logger
from common import download_image

def fetch_spacex_last_launch(launch_id: str = None, save_dir: str = "spacex_images") -> None:
    """Получает фотографии запуска SpaceX по ID или последнего запуска и сохраняет их локально.

    Args:
        launch_id (str, optional): Идентификатор запуска SpaceX в формате API v4.
            Если None, загружается последний запуск.
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
        print("Полный ответ API:", data)  # Диагностика
        image_urls = data.get("links", {}).get("flickr", {}).get("original", [])

        # Если в flickr.original нет фотографий, попробуем использовать patch
        if not image_urls:
            patch_urls = []
            patch_data = data.get("links", {}).get("patch", {})
            if patch_data.get("small"):
                patch_urls.append(patch_data["small"])
            if patch_data.get("large"):
                patch_urls.append(patch_data["large"])
            if patch_urls:
                image_urls = patch_urls
                logger.info(f"Используются патчи как изображения: {len(image_urls)}")
            else:
                # Если ни flickr, ни patch нет, используем запасной launch_id
                fallback_launch_id = "5eb87d47ffd86e000604b38a"
                fallback_url = f"https://api.spacexdata.com/v4/launches/{fallback_launch_id}"
                fallback_response = requests.get(fallback_url, timeout=30)
                fallback_response.raise_for_status()
                fallback_data = fallback_response.json()
                image_urls = fallback_data.get("links", {}).get("flickr", {}).get("original", [])
                if not image_urls:
                    patch_urls = []
                    patch_data = fallback_data.get("links", {}).get("patch", {})
                    if patch_data.get("small"):
                        patch_urls.append(patch_data["small"])
                    if patch_data.get("large"):
                        patch_urls.append(patch_data["large"])
                    if patch_urls:
                        image_urls = patch_urls
                        logger.info(f"Используются патчи из запасного запуска {fallback_launch_id}: {len(image_urls)}")
                    else:
                        logger.warning(f"Фотографий и патчей для последнего и запасного запуска не найдено.")
                        return
                else:
                    logger.info(f"Используются фотографии из запасного запуска {fallback_launch_id}: {len(image_urls)}")
                prefix = f"spacex_{fallback_launch_id}"

        logger.info(f"Найдено изображений: {len(image_urls)}")
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