import typer
import sys
from datetime import datetime

from loguru import logger


def main():
    today = datetime.today()
    week_of_year = int(today.strftime("%W"))

    if (week_of_year % 4) != 0:
        logger.info("Not a cleaning week. Stopping.")
        sys.exit(1)


if __name__ == "__main__":
    typer.run(main)
