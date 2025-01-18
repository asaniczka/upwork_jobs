""""""

from rich import print
from src.models.db_models import DBFreelancerIdentity
from src.models.upwork_models import FreelancerIdentity
from src.sqlalchemy.core_sqlalchemy import SESSIONMAKER


def update_freelancer_in_db(freelancer: FreelancerIdentity):
    """"""

    assert isinstance(
        freelancer, FreelancerIdentity
    ), f"Expected FreelancerIdentity, but got type {type(freelancer)}"

    print("Adding freelancer to db")
    with SESSIONMAKER() as session:
        # pylint:disable=not-an-iterable
        try:
            session.begin()
            db_freelancer = (
                session.query(DBFreelancerIdentity)
                .filter(DBFreelancerIdentity.cipher == freelancer.cipher)
                .first()
            )
            db_freelancer.country = freelancer.country
            db_freelancer.name = freelancer.name
            db_freelancer.user_id = freelancer.user_id
            db_freelancer.did_scrape = True
            db_freelancer.in_progress = False
            session.commit()
        except Exception as e:
            print("Error in a transaction", type(e), e)
            session.rollback()


def mark_freelancer_as_scraped(cipher: str):
    """"""

    print("Marking freelancer as done")
    with SESSIONMAKER() as session:
        # pylint:disable=not-an-iterable
        try:
            session.begin()
            db_freelancer = (
                session.query(DBFreelancerIdentity)
                .filter(DBFreelancerIdentity.cipher == cipher)
                .first()
            )
            db_freelancer.did_scrape = True
            db_freelancer.in_progress = False
            session.commit()
        except Exception as e:
            print("Error in a transaction", type(e), e)
            session.rollback()
