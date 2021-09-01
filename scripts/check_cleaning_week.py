import typer
import sys
import pendulum

from loguru import logger


def main():
    today = pendulum.now("America/Chicago")
    today_days_in_month = today.days_in_month
    days_left_in_month = today_days_in_month - today.day_of_month

    logger.info(
        f"Days in month for {today.strftime('%Y-%m-%d')}: "
        f"{days_left_in_month}."
    )
    if days_left_in_month >= 7:
        logger.info("Not a cleaning week. Stopping.")
        sys.exit(1)


if __name__ == "__main__":
    typer.run(main)
