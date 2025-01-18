"""module to update rows"""

# pylint:disable=wrong-import-position

import os
from urllib.parse import quote

import httpx
from dotenv import load_dotenv
from wrapworks import cwdtoenv

cwdtoenv()
load_dotenv()

from src.models.upwork_models import PostingAttributes


def update_row(url: str, attributes: PostingAttributes):
    """
    ### Description:
        - Updates a specific database row with new client data
          and job details.
        - Makes a PATCH request to the Upwork filtered jobs table
          to update the entry corresponding to the provided URL.

    ### Args:
        - `url`: str
            The URL of the job entry to update.
        - `attributes`: PostingAttributes
            The structured data containing updated job and client
            attributes.
    """

    print(f"Updating row {url}")

    url = (
        os.getenv("POSTGREST_URL") + "/upwork_filtered_jobs" + "?link=eq." + quote(url)
    )

    payload = {
        "client_city": attributes.client.client_city,
        "client_join_data": str(attributes.client.client_join_date),
        "client_jobs_posted": attributes.client.client_jobs_posted,
        "client_hire_rate": attributes.client.client_hire_rate,
        "client_open_jobs": attributes.client.client_open_jobs,
        "client_total_spent_usd": attributes.client.client_total_spent_usd,
        "client_total_hires": attributes.client.client_total_hires,
        "client_active_hires": attributes.client.client_active_hires,
        "client_avg_hourly_rate": attributes.client.client_avg_hourly_rate,
        "client_total_paid_hours": attributes.client.client_total_paid_hours,
        "did_augment_client_data": True,
    }
    headers = {
        "apikey": os.getenv("SUPABASE_CLIENT_ANON_KEY"),
        "Authorization": f"Bearer {os.getenv('SUPABASE_CLIENT_ANON_KEY')}",
        "Content-Type": "application/json",
    }

    response = httpx.patch(url, json=payload, headers=headers)


def update_row_as_done(url: str):
    """
    ### Description:
        - Marks a specific row in the database as done by updating
          the `did_augment_client_data` status to True.
        - Makes a PATCH request to the Upwork filtered jobs table
          for the specified job URL.

    ### Args:
        - `url`: str
            The URL of the job entry to mark as done.
    """

    print(f"Updating row {url} as done")

    url = (
        os.getenv("POSTGREST_URL") + "/upwork_filtered_jobs" + "?link=eq." + quote(url)
    )

    payload = {
        "did_augment_client_data": True,
    }
    headers = {
        "apikey": os.getenv("SUPABASE_CLIENT_ANON_KEY"),
        "Authorization": f"Bearer {os.getenv('SUPABASE_CLIENT_ANON_KEY')}",
        "Content-Type": "application/json",
    }

    response = httpx.patch(url, json=payload, headers=headers)


def update_hire_history_as_done(url: str):
    """"""

    print(f"Updating row {url} as hire history done")

    url = (
        os.getenv("POSTGREST_URL") + "/upwork_filtered_jobs" + "?link=eq." + quote(url)
    )

    payload = {"got_hire_history": True}
    headers = {
        "apikey": os.getenv("SUPABASE_CLIENT_ANON_KEY"),
        "Authorization": f"Bearer {os.getenv('SUPABASE_CLIENT_ANON_KEY')}",
        "Content-Type": "application/json",
    }

    response = httpx.patch(url, json=payload, headers=headers)


if __name__ == "__main__":
    import json

    url = "https://www.upwork.com/jobs/Azure-Communication-Services-Expert_%7E01ca8dd0ca558e3386?source=rss"
    with open("attr.json", "r", encoding="utf-8") as rf:
        attr = PostingAttributes(**json.load(rf))
        update_row(url, attr)
