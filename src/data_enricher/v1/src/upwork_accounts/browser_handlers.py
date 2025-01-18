import time

from bs4 import BeautifulSoup
from rich import print
from src.upwork_accounts.browser_worker import (
    get_cookies,
    get_driver,
    login,
    restart_session,
    save_cookies,
)


def get_page(url: str) -> str | None:
    """
    ### Description:
        - Loads a webpage using Selenium and returns the text
          content of the page.
        - Automatically refreshes the page with saved cookies.

    ### Args:
        - `url`: str
            The URL of the page to load.

    ### Returns:
        - `str | None`
            The text content of the page, or None if the page
            could not be loaded.
    """

    session_reset = False
    retries = 0
    while retries < 10:
        if retries > 5 and not session_reset:
            restart_session()
            session_reset = True

        print(f"Getting page {url}")
        try:
            driver = get_driver()
            driver.get(url)

            cookies = get_cookies()
            for i in cookies:
                driver.add_cookie(i)
            driver.refresh()
            time.sleep(10)

            source = driver.page_source
            save_cookies(driver.get_cookies())
            driver.quit()

            soup = BeautifulSoup(source, "html.parser")
            return soup.get_text(separator="\n")
        except Exception as e:
            try:
                driver.quit()
            except:
                pass
            print("Error when getting page", type(e).__name__, e)
            retries += 1


def do_login():
    """"""

    retries = 0
    while retries < 10:
        print("Trying to login to account")
        try:
            login()
            break
        except Exception as e:
            print("Error when logging in", type(e).__name__, e)
            retries += 1
