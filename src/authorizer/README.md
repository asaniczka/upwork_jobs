# Authenticator Lambda

This package contains an AWS Lambda function that serves as an authorizer within a larger ecosystem. Its primary function is to retrieve an authorization token from Zyte, publish it to PostgREST, and act as a REST endpoint to return the token to the invoker. The acquired token is saved to a PostgreSQL database to optimize costs associated with fetching tokens.

## Table of Contents

- [Overview](#overview)
- [Architecture Diagram](#architecture-diagram)

## Overview

The Authenticator Lambda function handles the lifecycle of obtaining an authentication token and validating requests. This function operates as follows:

1. **REST Endpoint**: It exposes a REST endpoint, allowing clients to invoke it and fetch an authorization token.
2. **Request Validation**: It validates incoming requests using a secret stored in environment variables, ensuring that only authorized entities can retrieve the token.
3. **Token Retrieval**: It fetches the necessary cookies from Zyte to extract the authorization token.
4. **Token Publishing**: The retrieved token is published to a designated PostgREST endpoint for storage in a PostgreSQL database.
5. **Token Caching**: By saving the token in PostgreSQL, the function minimizes the frequency of calls to Zyte, which can be costly. This caching mechanism allows other workers in the ecosystem to access the already fetched token without incurring additional costs.
6. **Response**: Finally, it returns the token to the invoker along with a status code.

## Architecture Diagram

```plaintext
+-----------------------+
|   Client Application  |
+-----------+-----------+
            |
            v
+-----------------------+
|      AWS Lambda       |
|     Authenticator     |
|    (REST Endpoint)    |
+-----------+-----------+
            |
            v
+-----------------------+
|       Zyte API       |
+-----------------------+
            |
            v
+-----------------------+
|       PostgREST       |
|    (Token Tracker)    |
|    + PostgreSQL DB    |
+-----------------------+
```

With this architecture, the Authenticator Lambda provides a seamless and cost-effective way to manage authorization tokens within your application ecosystem, significantly reducing the cost of repeated token fetching.
