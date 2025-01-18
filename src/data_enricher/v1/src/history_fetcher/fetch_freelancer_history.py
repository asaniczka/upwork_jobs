""""""

# pylint: disable = wrong-import-position

import json
import traceback

import httpx
import ua_generator
from dotenv import load_dotenv
from pydantic import ValidationError
from rich import print
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from wrapworks import cwdtoenv

load_dotenv()
cwdtoenv()

from src.errors.common_errors import NotLoggedIn
from src.models.upwork_models import FreelancerIdentity, WorkHistory
from src.sqlalchemy.insert_functions import save_work_history_to_db
from src.upwork_accounts.browser_worker import get_cookies


def get_profile(cipher: str) -> dict:

    url = (
        f"https://www.upwork.com/freelancers/api/v1/freelancer/profile/{cipher}/details"
    )

    params = {"excludeAssignments": "true"}

    headers = {
        "User-Agent": ua_generator.generate().text,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-GB,en;q=0.7,en-US;q=0.3",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": f"https://www.upwork.com/freelancers/{cipher}",
        "x-odesk-user-agent": "oDesk LM",
        "x-requested-with": "XMLHttpRequest",
        "Cookie": "; ".join(
            f"{key}={value}"
            for key, value in get_cookies(make_simple_dict=True).items()
        ),
    }

    print(headers)

    response = httpx.get(url, headers=headers, params=params)
    return response.json()


def get_profile_with_render(cipher: str, driver: Chrome) -> dict:

    url = (
        f"https://www.upwork.com/freelancers/api/v1/freelancer/profile/{cipher}/details"
    )

    driver.get(url)
    content = driver.page_source
    content = driver.find_element(By.CSS_SELECTOR, "pre")
    parsed_json = json.loads(content.text)

    return parsed_json


def get_contracts(user_id: str, in_progress: bool = False) -> dict:

    url = f"https://www.upwork.com/freelancers/api/v3/freelancer/profile/{user_id}/work-history/"

    if in_progress:
        url += "in-progress"
    else:
        url += "completed"

    params = {"page": "1", "limit": "50", "sortByAsNumber": "1", "filterPtc": "0"}
    headers = {
        "User-Agent": ua_generator.generate(
            device=("desktop"), browser=("chrome")
        ).text,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-GB,en;q=0.7,en-US;q=0.3",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://www.upwork.com/freelancers",
        "x-odesk-user-agent": "oDesk LM",
        "x-requested-with": "XMLHttpRequest",
        "Cookie": "; ".join(
            f"{key}={value}"
            for key, value in get_cookies(make_simple_dict=True).items()
        ),
    }

    response = httpx.get(url, headers=headers, params=params)

    print(response.status_code)
    if response.status_code == 200:
        return response.json()


def get_contracts_with_render(
    user_id: str, driver: Chrome, in_progress: bool = False
) -> dict:

    url = f"https://www.upwork.com/freelancers/api/v3/freelancer/profile/{user_id}/work-history/"

    if in_progress:
        url += "in-progress"
    else:
        url += "completed"

    driver.get(url)
    content = driver.page_source
    try:
        content = driver.find_element(By.CSS_SELECTOR, "pre")
    except Exception as e:
        print("Error getting json", content)
    parsed_json = json.loads(content.text)

    return parsed_json


def handle_freelancer_profile(cipher: str) -> FreelancerIdentity | None:
    """"""

    print(f"Processing freelancer {cipher}")

    profile = get_profile(cipher)
    if not profile:
        print("No response for freelancer from Upwork")
        return

    print(profile)
    if "error" in profile and "Refresh the page and sign in again" in profile["error"]:
        raise NotLoggedIn()

    # dump_json("profile.json", profile)
    freelancer = FreelancerIdentity(**profile)
    print(freelancer)

    timelines = ["in-progress", "completed"]
    for timeline in timelines:
        try:
            res = get_contracts(freelancer.user_id, timeline == "in-progress")
            if not res:
                print(f"No response from Upwork for {timeline}")
                continue

            if "details" in res and "not authenticated" in res.get("details", ""):
                raise NotLoggedIn()

            work_history = WorkHistory(**res)
            work_history.add_freelancer_data(
                name=freelancer.name, uid=freelancer.cipher
            )
            print(
                f"This freelancer has {len(work_history.work_history)} {timeline} hires"
            )
            save_work_history_to_db(work_history)
        except ValidationError:
            raise
        except Exception as e:
            traceback.print_exc()
            print(
                f"Error processing {timeline} of a freelancer",
                cipher,
                type(e).__name__,
                e,
            )
    return freelancer


def handle_freelancer_profile_rendered(
    cipher: str, driver: Chrome
) -> FreelancerIdentity | None:
    """"""

    print(f"Processing freelancer {cipher}")

    profile = get_profile_with_render(cipher, driver)
    if not profile:
        print("No response for freelancer from Upwork")
        return

    if "error" in profile and "Refresh the page and sign in again" in profile["error"]:
        raise NotLoggedIn()

    # dump_json("profile.json", profile)
    freelancer = FreelancerIdentity(**profile)

    timelines = ["in-progress", "completed"]
    for timeline in timelines:
        try:
            res = get_contracts_with_render(
                freelancer.user_id, driver, timeline == "in-progress"
            )
            if not res:
                print(f"No response from Upwork for {timeline}")
                continue

            if "details" in res and "not authenticated" in res.get("details", ""):
                raise NotLoggedIn()

            work_history = WorkHistory(**res)
            work_history.add_freelancer_data(
                name=freelancer.name, uid=freelancer.cipher
            )
            print(
                f"This freelancer has {len(work_history.work_history)} {timeline} hires"
            )
            save_work_history_to_db(work_history)
        except ValidationError:
            continue
        except NotLoggedIn:
            raise
        except Exception as e:
            traceback.print_exc()
            print(
                f"Error processing {timeline} of a freelancer",
                cipher,
                type(e).__name__,
                e,
            )
    return freelancer


if __name__ == "__main__":
    cipher = "~01592aa972f39bdeae"

    # handle_freelancer_profile_rendered(cipher)
