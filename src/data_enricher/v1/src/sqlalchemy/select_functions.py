""""""

# pylint:disable=wrong-import-position

from dotenv import load_dotenv
from rich import print
from sqlalchemy import select, text
from wrapworks import cwdtoenv

cwdtoenv()
load_dotenv()

from src.models.db_models import DBFreelancerIdentity
from src.sqlalchemy.core_sqlalchemy import SESSIONMAKER


def get_freelancer_from_db() -> str | None:
    """"""

    print("Getting freelancer from db")
    with SESSIONMAKER() as session:

        db_freelancer = (
            session.query(DBFreelancerIdentity)
            .filter(DBFreelancerIdentity.did_scrape != True)
            .first()
        )
        if db_freelancer:
            return db_freelancer.cipher
        return None


def get_batch_freelancers_from_db(limit=10) -> list[str] | None:

    print(f"Getting {limit} freelancers from db")
    with SESSIONMAKER() as session:

        stmt = text(
            """WITH
                temp_cte AS (
                    SELECT
                    cipher
                    FROM
                    upwork_freelancer_identity
                    WHERE
                    did_scrape IS FALSE
                    AND in_progress IS FALSE
                    LIMIT :limit
                    FOR UPDATE
                )
                UPDATE upwork_freelancer_identity
                SET
                in_progress = TRUE
                WHERE
                cipher IN (
                    SELECT
                    cipher
                    FROM
                    temp_cte
                )
                RETURNING
                cipher
                """
        )

        result = session.execute(stmt, {"limit": limit}).fetchall()
        session.commit()
        if result:
            return [x[0] for x in result]
        return None


def learn():

    with SESSIONMAKER() as session:

        stmt = (
            select(
                DBFreelancerIdentity.name,
                DBFreelancerIdentity.cipher,
                DBFreelancerIdentity.country,
            )
            .where(DBFreelancerIdentity.did_scrape == True)
            .where(DBFreelancerIdentity.name.ilike("%Lina%"))
            .limit(5)
        )
        res = session.execute(stmt)
        for i in res:
            print(i)


if __name__ == "__main__":
    print(get_batch_freelancers_from_db(1))
