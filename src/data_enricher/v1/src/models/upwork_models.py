import json
from datetime import datetime
from uuid import uuid4

import pytz
from pydantic import (
    AliasChoices,
    AliasPath,
    BaseModel,
    Field,
    HttpUrl,
    field_serializer,
    model_validator,
)


class UpworkClient(BaseModel):
    """
    pydantic model to store client data
    """

    client_country: str
    client_city: str | None = None
    client_join_date: datetime
    client_jobs_posted: int | None = None
    client_hire_rate: int | None = None
    client_open_jobs: int | None = None
    client_total_spent_usd: int | None = None
    client_total_hires: int | None = None
    client_active_hires: int | None = None
    client_avg_hourly_rate: float | None = None
    client_total_paid_hours: int | None = None

    @field_serializer("client_join_date", when_used="json")
    @classmethod
    def _date2str(cls, value: datetime) -> str:

        return str(value.date)


class UpworkJob(BaseModel):
    """
    Pydantic model to store job data
    """

    url: HttpUrl | None = None
    title: str
    full_description: str | None = None
    is_hourly: bool | None = None
    hourly_low: int | None = None
    hourly_high: int | None = None
    budget: int | None = None
    duration_months: int | None = None
    freelancer_experince_level: str | None = None
    project_type: str | None = None
    proposals: int = 0
    interviewing: int = 0
    invites_sent: int = 0
    unanswered_invites: int = 0


class PostingAttributes(BaseModel):
    job: UpworkJob
    client: UpworkClient


OPENAPI_SCHEMA = json.dumps(PostingAttributes.model_json_schema())


class PastJob(BaseModel):
    job_id: str | None = Field(
        validation_alias=AliasChoices(
            AliasPath("jobInfo", "ciphertext"), AliasPath("openingUid")
        )
    )
    is_fake_job_id: bool = False
    job_title: str = Field(
        validation_alias=AliasChoices(AliasPath("jobInfo", "title"), AliasPath("title"))
    )
    start_date: datetime | None = Field(
        validation_alias=AliasChoices(AliasPath("startDate"), AliasPath("startedOn"))
    )
    end_date: datetime | None = Field(
        validation_alias=AliasChoices(AliasPath("endDate"), AliasPath("endedOn"))
    )
    duration_days: int | None = None
    freelancer_name: str | None = Field(
        None, validation_alias=AliasPath("contractorInfo", "contractorName")
    )
    freelancer_id: str | None = Field(
        None, validation_alias=AliasPath("contractorInfo", "ciphertext")
    )
    is_fake_freelancer_id: bool = False
    total_hours: float = Field(validation_alias=AliasPath("totalHours"))
    total_paid: float = Field(
        0,
        validation_alias=AliasChoices(
            AliasPath("totalCharges", "amount"), AliasPath("totalCharge")
        ),
    )
    hourly_rate: float | None = Field(
        validation_alias=AliasChoices(
            AliasPath("rate", "amount"),
            AliasPath("rate"),
            AliasPath("hourlyRate", "amount"),
            AliasPath("hourlyRate"),
        )
    )

    @model_validator(mode="after")
    def _validate_id(self):

        if not self.job_id:
            self.job_id = str(uuid4())
            self.is_fake_job_id = True

        if not self.freelancer_id:
            self.freelancer_id = str(uuid4())
            self.is_fake_freelancer_id = True

        return self

    @model_validator(mode="after")
    def _count_contract_days(self):

        if self.start_date and self.end_date:
            duration = self.end_date - self.start_date
            self.duration_days = duration.days
        elif self.start_date:
            end_date = datetime.now(pytz.UTC)
            duration = end_date - self.start_date
            self.duration_days = duration.days

        return self


class FreelancerIdentity(BaseModel):
    cipher: str = Field(validation_alias=AliasPath("profile", "identity", "ciphertext"))
    user_id: str = Field(validation_alias=AliasPath("profile", "identity", "uid"))
    name: str = Field(validation_alias=AliasPath("profile", "profile", "name"))
    country: str = Field(
        validation_alias=AliasPath("profile", "profile", "location", "country")
    )


class WorkHistory(BaseModel):
    work_history: list[PastJob] = Field(
        validation_alias=AliasChoices(AliasPath("workHistory"), AliasPath("pageItems")),
        default_factory=list,
    )

    def add_freelancer_data(self, name: str, uid: str):
        # pylint:disable=not-an-iterable
        for contract in self.work_history:
            contract.freelancer_name = name
            contract.freelancer_id = uid
            contract.is_fake_freelancer_id = False
            contract.is_fake_job_id = True
