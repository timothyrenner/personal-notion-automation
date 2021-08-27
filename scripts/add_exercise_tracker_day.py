import typer
import os
import sys
import requests

from dotenv import load_dotenv, find_dotenv
from loguru import logger

logger.info("Loading .env file.")
load_dotenv(find_dotenv())
NOTION_KEY = os.getenv("NOTION_KEY")
if not NOTION_KEY:
    logger.error(
        "No entry for NOTION_KEY in .env or environment. Terminating."
    )
    sys.exit(1)

EXERCISE_TRACKER_DATABASE_ID = os.getenv("NOTION_EXERCISE_TRACKER_DATABASE_ID")
if not EXERCISE_TRACKER_DATABASE_ID:
    logger.error(
        "No entry for NOTION_EXERCISE_TRACKER_DATABASE_ID in .env or "
        "environment. Terminating."
    )
    sys.exit(1)

NOTION_URL = "https://api.notion.com"


def main(name: str = typer.Option(...), date: str = typer.Option(...)):
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"Bearer {NOTION_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": "2021-08-16",
        }
    )
    create_record_payload = {
        "parent": {"database_id": EXERCISE_TRACKER_DATABASE_ID},
        "properties": {
            "Name": {"title": [{"type": "text", "text": {"content": name}}]},
            "Date": {"date": {"start": date, "end": None}},
        },
    }
    logger.info("Creating record.")
    response = session.post(
        f"{NOTION_URL}/v1/pages", json=create_record_payload
    )
    if not response.ok:
        logger.error(response.json())
    logger.info("💪 page created successfully 💪 ")


if __name__ == "__main__":
    typer.run(main)
