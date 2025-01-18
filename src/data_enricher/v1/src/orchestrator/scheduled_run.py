"""Runs the manual orchestrator on a schedule"""

# pylint:disable=wrong-import-position

import time

from dotenv import load_dotenv
from wrapworks import cwdtoenv

cwdtoenv()
load_dotenv()

from src.orchestrator.manual_run import (
    client_data_executor,
    freelancer_history_executor,
    hire_history_executor,
)
from src.upwork_accounts.browser_handlers import do_login


def executor():
    """"""

    do_login()

    callables = [
        client_data_executor,
        hire_history_executor,
        freelancer_history_executor,
    ]
    while True:
        for call in callables:
            try:
                call()
            except Exception as e:
                print("Error in a callable", call.__name__, type(e), e)

        print("Sleeping 15")
        time.sleep(15 * 60)


if __name__ == "__main__":
    executor()
