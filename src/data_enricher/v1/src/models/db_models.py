""""""

from datetime import datetime
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TIMESTAMP


class Base(DeclarativeBase):
    pass


class DBUpworkContracts(Base):
    __tablename__ = "upwork_contracts"

    job_id: Mapped[str] = mapped_column(primary_key=True)
    is_fake_job_id: Mapped[bool]
    job_title: Mapped[str]
    start_date: Mapped[datetime]
    end_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    duration_days: Mapped[Optional[int]] = mapped_column(nullable=True)
    freelancer_name: Mapped[str]
    freelancer_id: Mapped[str]
    is_fake_freelancer_id: Mapped[bool]
    total_hours: Mapped[float]
    total_paid: Mapped[float]
    hourly_rate: Mapped[Optional[float]] = mapped_column(nullable=True)
    inserted_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.now
    )

    __table_args__ = (
        UniqueConstraint(
            "job_title",
            "freelancer_id",
            name="unique_upwork_contracts_jobtitle_freelancerid",
        ),
    )


class DBFreelancerIdentity(Base):

    __tablename__ = "upwork_freelancer_identity"

    cipher: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(nullable=True)
    country: Mapped[str] = mapped_column(nullable=True)
    did_scrape: Mapped[bool] = mapped_column(default=False)
    in_progress: Mapped[bool] = mapped_column(default=False)
    first_seen: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.now
    )

    def __repr__(self) -> str:
        return f"{self.cipher}: {self.name} - {self.country}"
