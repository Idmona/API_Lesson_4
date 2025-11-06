import logging

logger = logging.getLogger(__name__)


def main():
    """Настройка логирования при прямом запуске файла."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger.info("Логер успешно настроен и запущен.")


if __name__ == "__main__":
    main()
