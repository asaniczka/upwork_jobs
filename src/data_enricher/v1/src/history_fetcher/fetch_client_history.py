""""""

# pylint: disable = wrong-import-position
import traceback

import httpx
import ua_generator
from dotenv import load_dotenv
from rich import print
from wrapworks import cwdtoenv

load_dotenv()
cwdtoenv()

from src.errors.common_errors import NotLoggedIn
from src.models.upwork_models import WorkHistory
from src.sqlalchemy.insert_functions import save_work_history_to_db
from src.upwork_accounts.browser_worker import get_cookies


def get_history(cipher: str) -> dict:

    url = f"https://www.upwork.com/job-details/jobdetails/api/job/{cipher}/details"

    headers = {
        "User-Agent": ua_generator.generate(
            device=("desktop"), browser=("chrome")
        ).text,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-GB,en;q=0.7,en-US;q=0.3",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": f"https://www.upwork.com/nx/find-work/details/{cipher}",
        "x-odesk-user-agent": "oDesk LM",
        "x-requested-with": "XMLHttpRequest",
        "Cookie": "; ".join(
            f"{key}={value}"
            for key, value in get_cookies(make_simple_dict=True).items()
        ),
    }

    response = httpx.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()


def handle_single_client(cipher: str):
    """"""

    print(f"Fetching hire history of {cipher}")

    try:
        res = get_history(cipher)
        if not res:
            print("No response from Upwork")
            return

        if "details" in res and "not authenticated" in res.get("details", ""):
            raise NotLoggedIn()

        work_history = WorkHistory(**res)
        print(f"This client has {len(work_history.work_history)} past hires")
        save_work_history_to_db(work_history)
    except NotLoggedIn:
        raise

    except Exception as e:
        traceback.print_exc()
        print("Error processing a client", cipher, type(e).__name__, e)


if __name__ == "__main__":
    cipher = "~01ca8dd0ca558e3386"
    handle_single_client(cipher)
