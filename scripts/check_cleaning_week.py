import typer
import sys
import pendulum

from loguru import logger


def main():
    today = pendulum.now()
    if today.week_of_month > 1:
        logger.info("Not a cleaning week. Stopping.")
        sys.exit(1)


if __name__ == "__main__":
    typer.run(main)
