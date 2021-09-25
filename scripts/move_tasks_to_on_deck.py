import typer
import os
import sys
import requests

from dotenv import load_dotenv, find_dotenv
from loguru import logger
from typing import List

logger.info("Loading .env file.")
load_dotenv(find_dotenv())
NOTION_KEY = os.getenv("NOTION_KEY")
if not NOTION_KEY:
    logger.error(
        "No entry for NOTION_KEY in .env or environment. Terminating."
    )
    sys.exit(1)

NOTION_URL = "https://api.notion.com"
TASKS_DATABASE_ID = os.getenv("NOTION_TASKS_DATABASE_ID")
if not TASKS_DATABASE_ID:
    logger.error(
        "No entry for NOTION_TASKS_DATABASE_ID in .env or environment. "
        "Terminating."
    )
    sys.exit(1)


def get_in_progress_tasks(
    session: requests.Session, database_id: str
) -> List[str]:

    query_payload = {
        "filter": {
            "and": [{"property": "Status", "select": {"equals": "Doing"}}]
        }
    }

    query_response = session.post(
        f"{NOTION_URL}/v1/databases/{database_id}/query", json=query_payload
    )

    if not query_response.ok:
        logger.error("Unable to perform query for in progress tasks.")
        logger.error(query_response.json())
        sys.exit(1)

    query_response_json = query_response.json()
    task_ids = [x["id"] for x in query_response_json["results"]]
    return task_ids


def set_to_on_deck(session: requests.Session, task_id: str):

    update_payload = {
        "properties": {"Status": {"select": {"name": "On Deck"}}}
    }

    update_response = session.patch(
        f"{NOTION_URL}/v1/pages/{task_id}", json=update_payload
    )

    if not update_response.ok:
        logger.error("Unable to update task.")
        logger.error(update_response.json())
        sys.exit(1)


def main():
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"Bearer {NOTION_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": "2021-08-16",
        }
    )

    logger.info("Obtaining in progress tasks.")
    in_progress_tasks = get_in_progress_tasks(session, TASKS_DATABASE_ID)
    for task_id in in_progress_tasks:
        logger.info("Setting task to 'On Deck'.")
        set_to_on_deck(session, task_id)


if __name__ == "__main__":
    typer.run(main)
