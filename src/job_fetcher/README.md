# Job Fetcher Lambda

This package contains an AWS Lambda function dedicated to fetching job postings from the Upwork public job board. This function acts as a publisher of jobs, collecting all job postings and saving them to a PostgreSQL database specified by your configuration. It is designed to run on a schedule, triggered via Amazon EventBridge.

## Table of Contents

- [Overview](#overview)
- [Architecture Diagram](#architecture-diagram)

## Overview

The Job Fetcher Lambda function performs the following key responsibilities:

1. **Scheduled Invocation**: It is triggered on a specified schedule using Amazon EventBridge, allowing for regular updates of job postings.

2. **Token Management**: It first attempts to retrieve an authorization token from a PostgreSQL database cache. If the cached token is unavailable or fails, it falls back to using the Authenticator Lambda to fetch a new token.

3. **Job Collection**: It constructs a query to fetch job postings from the Upwork API, collecting essential information such as job title, description, required skills, and budget details.

4. **Database Upload**: The collected job data is uploaded in parallel to a PostgreSQL database for storage, ensuring efficient handling of multiple job entries at once.

5. **Cost Efficiency**: By caching job postings in the database and only fetching new jobs on a regular schedule, this function minimizes API calls to Upwork, reducing the associated costs and ensuring the efficient retrieval of job postings.

## Architecture Diagram

```plaintext
+-----------------------+
|     AWS Eventbridge   |
+-----------+-----------+
            |
            v
+-----------------------+
|      AWS Lambda       |
|      Job Fetcher      |
+-----------+-----------+
            |
            v
+-----------------------+
|       Upwork API      |
+-----------------------+
            |
            v
+-----------------------+
|       PostgREST       |
|      (Job Storage)    |
|     + PostgreSQL DB   |
+-----------------------+
```


This architecture allows the Job Fetcher Lambda function to efficiently manage job postings by prioritizing cached tokens, thereby enhancing performance and cost-effectiveness when retrieving job opportunities from Upwork.
