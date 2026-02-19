import logging
import os


def configure_logging(service_name: str) -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format=f"%(asctime)s %(levelname)s [{service_name}] %(message)s",
    )
