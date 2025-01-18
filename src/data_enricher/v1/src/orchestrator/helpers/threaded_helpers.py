"""
Module to manually trigger data augmentation
"""

# pylint:disable=wrong-import-position
from rich import print
from src.errors.common_errors import NotLoggedIn
from src.formatter.format_cipher import get_cipher
from src.history_fetcher.fetch_client_history import handle_single_client
from src.history_fetcher.fetch_freelancer_history import (
    handle_freelancer_profile_rendered,
)
from src.postgres.update_functions import update_hire_history_as_done
from src.sqlalchemy.update_functions import (
    mark_freelancer_as_scraped,
    update_freelancer_in_db,
)
from src.upwork_accounts.browser_handlers import do_login


def handler_freelancer_history_threaded(cipher: str):
    """"""
    try:
        freelancer = handle_freelancer_profile_rendered(cipher)
        update_freelancer_in_db(freelancer)
    except NotLoggedIn:
        raise
    except Exception as e:
        print("Unable to get freelancer history: ", cipher, type(e).__name__, e)
        mark_freelancer_as_scraped(cipher)


def handler_hire_history_threaded(url):
    """"""

    try:
        cipher = get_cipher(url)
        handle_single_client(cipher)
        update_hire_history_as_done(url)
    except NotLoggedIn:
        do_login()
        return
    except Exception as e:
        print("Unable to get hire history: ", url, type(e).__name__, e)
        update_hire_history_as_done(url)
