import argparse
import logging
from typing import Callable, Dict, Any

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_script(
        description: str,
        main_func: Callable[..., None],
        default_args: Dict[str, Any],
        api_key_required: bool = False
) -> None:
    """Универсальная функция для обработки аргументов командной строки и запуска скрипта.

    Args:
        description (str): Описание скрипта для парсера аргументов.
        main_func (Callable[..., None]): Основная функция скрипта.
        default_args (Dict[str, Any]): Словарь с аргументами и их значениями по умолчанию.
        api_key_required (bool, optional): Требуется ли API-ключ. По умолчанию False.
    """
    parser = argparse.ArgumentParser(description=description)

    for arg_name, arg_config in default_args.items():
        parser.add_argument(
            f"--{arg_name}",
            type=arg_config["type"],
            default=arg_config["default"],
            help=arg_config["help"]
        )

    if api_key_required:
        parser.add_argument(
            "--api_key",
            type=str,
            help="API-ключ (если не указан — берётся из .env)"
        )

    args = parser.parse_args()

    try:
        if api_key_required:
            from common import get_api_key
            args_dict = vars(args)
            args_dict["api_key"] = get_api_key("NASA_API_KEY", args.api_key)
            main_func(**args_dict)
        else:
            main_func(**vars(args))
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        raise