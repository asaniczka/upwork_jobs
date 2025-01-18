"""
### Description:
- This module is responsible for augmenting client data related to job postings on Upwork.
- It fetches client details and updates database records.
"""

import asyncio
import json
import os
import random
from datetime import datetime

import httpx
import ua_generator
from dotenv import load_dotenv
from pydantic import (
    AliasChoices,
    AliasPath,
    BaseModel,
    Field,
    ValidationError,
    field_validator,
)
from rich import print

load_dotenv()


class UpworkClient(BaseModel):
    """
    ### Description:
    - Represents an Upwork client with various statistics
      related to their hiring and spending on freelancers.
    """

    client_country: str | None = Field(
        validation_alias=AliasPath("buyer", "location", "country")
    )
    client_city: str | None = Field(
        validation_alias=AliasPath("buyer", "location", "city")
    )
    client_join_date: datetime | None = Field(
        validation_alias=AliasPath("buyer", "company", "contractDate")
    )
    client_jobs_posted: int | None = Field(
        validation_alias=AliasPath("buyer", "jobs", "postedCount")
    )
    client_open_jobs: int | None = Field(
        validation_alias=AliasPath("buyer", "jobs", "openCount")
    )
    client_total_spent_usd: float | int | None = Field(
        validation_alias=AliasChoices(
            AliasPath("buyer", "stats", "totalCharges", "amount"),
            AliasPath("buyer", "stats", "totalCharges"),
        )
    )
    client_total_hires: int | None = Field(
        validation_alias=AliasPath("buyer", "stats", "totalJobsWithHires")
    )
    client_active_hires: int | None = Field(
        validation_alias=AliasPath("buyer", "stats", "activeAssignmentsCount")
    )
    client_avg_hourly_rate: float | None = Field(
        validation_alias=AliasChoices(
            AliasPath("buyer", "avgHourlyJobsRate", "amount"),
            AliasPath("buyer", "avgHourlyJobsRate"),
        )
    )
    client_total_paid_hours: int | float | None = Field(
        validation_alias=AliasPath("buyer", "stats", "hoursCount"),
    )

    @field_validator(
        "client_total_spent_usd",
        "client_avg_hourly_rate",
        "client_total_paid_hours",
        mode="after",
    )
    @classmethod
    def _float2int(cls, value: float | None | int):

        if value is None:
            return None
        return int(value)


async def update_row(upwork_link: str, client: UpworkClient):
    """
    ### Description:
        - Asynchronously updates the client data in the database
          for a specific Upwork link.
        - Sends a PATCH request to the server with updated data.

    ### Args:
        - `upwork_link`: str
            The Upwork job link that needs to be updated.
        - `client`: UpworkClient
            The UpworkClient instance containing updated client data.

    """

    print(f"Updating row {upwork_link}")

    url = os.getenv("POSTGREST_URL") + "upwork_filtered_jobs"

    payload = {
        "client_city": client.client_city,
        "client_join_data": (
            str(client.client_join_date) if client.client_join_date else None
        ),
        "client_jobs_posted": client.client_jobs_posted,
        "client_open_jobs": client.client_open_jobs,
        "client_total_spent_usd": client.client_total_spent_usd,
        "client_total_hires": client.client_total_hires,
        "client_active_hires": client.client_active_hires,
        "client_avg_hourly_rate": client.client_avg_hourly_rate,
        "client_total_paid_hours": client.client_total_paid_hours,
        "did_augment_client_data": True,
    }
    headers = {
        "apikey": os.getenv("SUPABASE_CLIENT_ANON_KEY"),
        "Authorization": f"Bearer {os.getenv('SUPABASE_CLIENT_ANON_KEY')}",
        "Content-Type": "application/json",
    }
    params = {"link": "eq." + upwork_link}

    response = await httpx.AsyncClient(headers=headers).patch(
        url, json=payload, params=params
    )
    print(response.status_code)
    if response.status_code >= 400:
        print(response.text)


async def increase_try_count(upwork_link: str):
    """"""

    print("Increasing try count of a link")
    url = os.getenv("POSTGREST_URL") + "upwork_filtered_jobs"
    headers = {
        "apikey": os.getenv("SUPABASE_CLIENT_ANON_KEY"),
        "Authorization": f"Bearer {os.getenv('SUPABASE_CLIENT_ANON_KEY')}",
        "Content-Type": "application/json",
    }

    params = {
        "link": f"eq.{upwork_link}",
        "select": "client_data_try_count",
        "limit": 10,
    }
    response = await httpx.AsyncClient().get(url, headers=headers, params=params)

    rows = response.json()
    if not rows:
        return None

    print(rows)
    count = rows[0]["client_data_try_count"] + 1

    payload = {"client_data_try_count": count}
    params = {"link": "eq." + upwork_link}

    response = await httpx.AsyncClient().patch(
        url, headers=headers, json=payload, params=params
    )
    print(response.status_code)
    if response.status_code >= 400:
        print(response.text)


def get_pending_rows() -> list[str] | None:
    """
    ### Description:
        - Fetches a list of pending rows for client data augmentation
          from the database.

    ### Returns:
        - `list[str] | None`
            A list of Upwork links to augment, or None if none are found.
    """

    url = os.getenv("POSTGREST_URL") + "upwork_filtered_jobs"

    querystring = {
        "did_augment_client_data": "eq.false",
        "client_data_try_count": "lt.1",
        "select": "link",
        "limit": 10,
    }

    headers = {
        "apikey": os.getenv("SUPABASE_CLIENT_ANON_KEY"),
        "Authorization": f"Bearer {os.getenv('SUPABASE_CLIENT_ANON_KEY')}",
        "Content-Type": "application/json",
    }

    response = httpx.get(url, headers=headers, params=querystring)

    rows = response.json()
    if not rows:
        return None
    return [x["link"] for x in rows]


def download_proxies() -> list[str]:
    res = httpx.get(os.getenv("PROXY_URL"), timeout=5)
    return res.text.split()


def get_proxy(proxies: list[str]) -> str:
    """"""

    print("Getting a new proxy")

    proxy = random.choice(proxies)
    ip, port, user, password = proxy.split(":")

    return "http://" + user + ":" + password + "@" + ip + ":" + port


async def get_details(cipher: str, proxies: list[str]) -> UpworkClient:
    """
    ### Description:
        - Asynchronously fetches the details of a client
          from Upwork using their job cipher.

    ### Args:
        - `cipher`: str
            The cipher code for the Upwork job.

    ### Returns:
        - `UpworkClient`
            An instance containing the client's data.

    ### Raises:
        - `httpx.HTTPStatusError`:
            If the request fails due to an HTTP error.
    """

    url = f"https://www.upwork.com/job-details/jobdetails/visitor/{cipher}/details"

    headers = {
        "User-Agent": ua_generator.generate().text,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-GB,en;q=0.7,en-US;q=0.3",
        "x-odesk-user-agent": "oDesk LM",
        "x-requested-with": "XMLHttpRequest",
    }

    retries = 0
    while retries < 10:
        try:
            response = await httpx.AsyncClient(
                headers=headers, proxy=get_proxy(proxies), timeout=5
            ).get(url)

            if response.status_code == 407:
                raise RuntimeError("Invalid Proxy")
            break

        except (httpx.ProxyError, RuntimeError):
            retries += 1
            continue
    client = UpworkClient(**response.json())

    return client


def link_to_cipher(link: str) -> str:
    """
    ### Description:
        - Converts a given Upwork job link into its corresponding
          job cipher for further processing.

    ### Args:
        - `link`: str
            The Upwork job link to convert.

    ### Returns:
        - `str`
            The cipher code extracted from the job link.
    """
    return link.split("/")[-1]


async def handle_row(url: str, proxies: list[str]):
    """
    ### Description:
        - Handles the enrichment process for a single row of data,
        including retries in case of failures.

    ### Args:
        - `url`: str
            The Upwork job link to process.
    """
    await increase_try_count(url)
    retries = 0
    while retries < 3:
        try:
            details = await get_details(link_to_cipher(url), proxies)
            await update_row(url, details)
            break
        except ValidationError:
            retries += 1
        except Exception as e:
            print("Exception in a URL", url, type(e).__name__, e)
            retries += 1
    else:
        raise RuntimeError("Unable to process row")


async def async_handler(rows: list[str], proxies: list[str]):
    """
    ### Description:
        - Manages the asynchronous handling of multiple rows of
        client data augmentation.

    ### Args:
        - `rows`: list[str]
            A list of Upwork job links to process.
    """

    print(f"We have {len(rows)} to work on this round")

    tasks = [asyncio.Task(handle_row(x, proxies)) for x in rows]
    done, pending = await asyncio.wait(tasks, return_when="ALL_COMPLETED")

    completed = 0
    errors = 0
    for future in done:
        if future.exception():
            errors += 1
        else:
            completed += 1

    print(
        f"Out of {len(rows)} rows, {completed} rows completed successfully while {errors} failed"
    )


def lambda_handler(event, context):
    """
    ### Description:
        - Main handler function for AWS Lambda which retrieves
        pending rows and triggers the async processing.

    ### Args:
        - `event`: any
            Event data provided by AWS Lambda.
        - `context`: any
            Context providing runtime information.

    ### Returns:
        - `str`
            JSON string indicating the status of the operation.
    """
    rows = get_pending_rows()
    proxies = download_proxies()
    if not rows:
        print("No rows available")
        return json.dumps({"status_code": 200, "status": "No rows available"})
    asyncio.run(async_handler(rows, proxies))

    return json.dumps({"status_code": 200, "status": "Rows processed successfully"})


if __name__ == "__main__":
    lambda_handler(1, 1)
    # asyncio.run(increase_try_count("https://www.upwork.com/jobs/~019e435b7718f79a48"))
