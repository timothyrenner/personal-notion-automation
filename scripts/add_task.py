import typer
import os
import sys
import requests

from dotenv import load_dotenv, find_dotenv
from loguru import logger
from enum import Enum
from typing import List


class Status(str, Enum):
    to_do = "To Do"
    doing = "Doing"
    blocked = "Blocked"
    done = "Done"
    on_deck = "On Deck"


class Project(str, Enum):
    mle = "MLE"
    misc = "Misc"
    wellness = "Wellness"
    house = "House"


class TaskType(str, Enum):
    work = "work"
    coordination = "coordination"


logger.info("Loading .env file.")
load_dotenv(find_dotenv())
NOTION_KEY = os.getenv("NOTION_KEY")
if not NOTION_KEY:
    logger.error(
        "No entry for NOTION_KEY in .env or environment. Terminating."
    )
    sys.exit(1)
TASKS_DATABASE_ID = os.getenv("NOTION_TASKS_DATABASE_ID")
if not TASKS_DATABASE_ID:
    logger.error(
        "No entry for NOTION_TASKS_DATABASE_ID in .env or environment. "
        "Terminating."
    )
    sys.exit(1)
PROJECTS_DATABASE_ID = os.getenv("NOTION_PROJECTS_DATABASE_ID")
if not PROJECTS_DATABASE_ID:
    logger.error(
        "No entry for NOTION_PROJECTS_DATABASE_ID in .env or environment. "
        "Terminating."
    )
    sys.exit(1)

NOTION_URL = "https://api.notion.com"


def get_project_id(session: requests.Session, project_name: Project) -> str:
    logger.info("Obtaining project id.")
    project_query = session.post(
        f"{NOTION_URL}/v1/databases/{PROJECTS_DATABASE_ID}/query",
        json={
            "filter": {
                "and": [
                    {
                        "property": "Name",
                        "title": {"equals": project_name},
                    }
                ]
            }
        },
    )

    if not project_query.ok:
        logger.error("Unable to retrieve project id.")
        logger.error(project_query.json())
        sys.exit(1)

    project_query_json = project_query.json()
    if len(project_query_json["results"]) > 1:
        logger.warning(
            f"More than one project found for {project_name}."
            "Check the projects database."
        )
    project_id = project_query_json["results"][0]["id"]
    return project_id


def check_if_task_exists(
    session: requests.Session,
    name: str,
    project_ids: List[str],
    task_type: TaskType,
) -> bool:
    query = {
        "filter": {
            "and": [
                # Match any of the project ids...
                {
                    "or": [
                        {
                            "property": "Project",
                            "relation": {"contains": project_id},
                        }
                        for project_id in project_ids
                    ]
                },
                # ... and the name ...
                {"property": "Name", "title": {"equals": name}},
                # ... and the task type.
                {"property": "Type of Task", "select": {"equals": task_type}},
                # ... with status not equal to "Done.'
                {"property": "Status", "select": {"does_not_equal": "Done"}},
            ]
        }
    }

    query_response = session.post(
        f"{NOTION_URL}/v1/databases/{TASKS_DATABASE_ID}/query", json=query
    )

    if not query_response.ok:
        logger.error("Unable to perform query for identical tasks.")
        logger.error(query_response.json())
        sys.exit(1)

    query_response_json = query_response.json()

    return len(query_response_json["results"]) > 0


def create_record(
    session: requests.Session,
    name: str,
    status: Status,
    project_ids: List[str],
    task_type: TaskType,
):
    create_record_payload = {
        "parent": {"database_id": TASKS_DATABASE_ID},
        "properties": {
            "Name": {"title": [{"type": "text", "text": {"content": name}}]},
            "Status": {"select": {"name": status}},
            "Type of Task": {"select": {"name": task_type}},
            "Project": {"relation": [{"id": pid} for pid in project_ids]},
        },
    }

    response = session.post(
        f"{NOTION_URL}/v1/pages", json=create_record_payload
    )
    if not response.ok:
        logger.error(response.json())
        sys.exit(1)


def main(
    name: str = typer.Option(...),
    status: Status = typer.Option(...),
    project: List[Project] = typer.Option(...),
    task_type: TaskType = TaskType.work,
    skip_existing: bool = typer.Option(False, "--skip-existing"),
):
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"Bearer {NOTION_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": "2021-08-16",
        }
    )

    logger.info(f"Obtaining ID for {project}.")
    project_ids = [get_project_id(session, p) for p in project]

    skip_create = False

    if skip_existing:
        logger.info("Querying for identical tasks.")
        skip_create = check_if_task_exists(
            session, name, project_ids, task_type
        )

    if not skip_create:
        logger.info("Creating record.")
        create_record(session, name, status, project_ids, task_type)
    else:
        logger.info("Task exists. Skipping creation.")


if __name__ == "__main__":
    typer.run(main)
