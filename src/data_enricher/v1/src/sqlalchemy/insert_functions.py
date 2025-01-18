""""""

from rich import print
from sqlalchemy.exc import IntegrityError
from src.models.db_models import DBUpworkContracts
from src.models.upwork_models import WorkHistory
from src.sqlalchemy.core_sqlalchemy import SESSIONMAKER


def save_work_history_to_db(work_history: WorkHistory):
    """"""

    if not work_history.work_history:
        return

    assert isinstance(
        work_history, WorkHistory
    ), f"Expected WorkHistory, but got type {type(work_history)}"

    print("Adding work history to db")
    with SESSIONMAKER() as session:
        # pylint:disable=not-an-iterable
        for i in work_history.work_history:
            try:
                session.begin()
                job = i.model_dump()
                job = DBUpworkContracts(**job)
                session.merge(job)
                session.commit()
            except IntegrityError as e:
                session.rollback()
            except Exception as e:
                print("Error in a transaction", type(e), e)
                session.rollback()
