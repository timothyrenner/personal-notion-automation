import typer
import sys
import pendulum

from loguru import logger


def main():
    today = pendulum.now("America/Chicago")
    today_week_of_year = today.week_of_year

    logger.info(
        f"Week of year for {today.strftime('%Y-%m-%d')}: "
        f"{today_week_of_year}."
    )
    if today_week_of_year % 2 > 0:
        logger.info("Not a recycling week. Stopping.")
        sys.exit(1)


if __name__ == "__main__":
    typer.run(main)
