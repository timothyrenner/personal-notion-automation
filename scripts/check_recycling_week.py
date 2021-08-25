import typer
import sys
import pendulum

from loguru import logger


def main():
    today = pendulum.now("America/Chicago")
    today_week_of_month = today.week_of_month

    logger.info(
        f"Week of month for {today.strftime('%Y-%m-%d')}: "
        f"{today_week_of_month}."
    )
    if today_week_of_month not in {2, 4, 6}:
        logger.info("Not a recycling week. Stopping.")
        sys.exit(1)


if __name__ == "__main__":
    typer.run(main)
