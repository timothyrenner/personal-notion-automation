import typer
import os
import sys
import requests

from dotenv import load_dotenv, find_dotenv
from loguru import logger
from enum import Enum
from typing import List

logger.info("Loading .env file.")
load_dotenv(find_dotenv())
NOTION_KEY = os.getenv("NOTION_KEY")
if not NOTION_KEY:
    logger.error(
        "No entry for NOTION_KEY in .env or environment. Terminating."
    )
    sys.exit(1)
PERSONAL_TASKS_DATABASE_ID = os.getenv("NOTION_PERSONAL_TASKS_DATABASE_ID")
if not PERSONAL_TASKS_DATABASE_ID:
    logger.error(
        "No entry for NOTION_PERSONAL_TASKS_DATABASE_ID in .env or "
        "environment. Terminating."
    )

NOTION_URL = "https://api.notion.com"


class Project(str, Enum):
    open_source = "Open Source"
    medical = "Medical"
    house = "House"
    personal = "Personal"
    camping = "Camping"
    photography = "Photography"
    car = "Car"


class Status(str, Enum):
    to_do = "To Do"
    doing = "Doing"
    blocked = "Blocked"
    done = "Done"
    on_deck = "On Deck"


def main(
    name: str = typer.Option(...),
    status: Status = typer.Option(...),
    project: List[Project] = typer.Option(...),
):
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"Bearer {NOTION_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": "2021-08-16",
        }
    )

    create_record_payload = {
        "parent": {"database_id": PERSONAL_TASKS_DATABASE_ID},
        "properties": {
            "Name": {"title": [{"type": "text", "text": {"content": name}}]},
            "Status": {"select": {"name": status}},
            "Project": {"multi_select": [{"name": p} for p in project]},
        },
    }
    logger.info("Creating record.")
    session.post(f"{NOTION_URL}/v1/pages", json=create_record_payload)


if __name__ == "__main__":
    typer.run(main)
