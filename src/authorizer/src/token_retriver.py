"""Handles retrival of an Auth Token"""

import os
import httpx
from dotenv import load_dotenv
from rich import print
import json

load_dotenv()


def get_cookies() -> list[dict]:
    """
    ### Description:
        - Retrieves cookies from a specific API endpoint.
        - Calls the Zyte API to extract response cookies from the given URL.

    ### Returns:
        - `cookies`: list[dict]
            A list of dictionaries containing the cookies from the API response.

    ### Raises:
        - `httpx.HTTPStatusError`:
            If the API response indicates an error status code.
    """
    print("Calling Zyte")
    api_response = httpx.post(
        "https://api.zyte.com/v1/extract",
        auth=(os.getenv("ZYTE_KEY"), ""),
        json={
            "url": "https://www.upwork.com/nx/search/jobs/",
            "browserHtml": True,
            "responseCookies": True,
        },
        timeout=60,
    )

    if api_response.status_code != 200:
        print("Failure on Zyte: ", api_response.status_code, api_response.text)
    parsed_res = api_response.json()
    cookies: list[dict] = parsed_res["responseCookies"]
    return cookies


def extract_search_token(cookies: list[dict]) -> str:
    """
    ### Description:
        - Extracts the search token and its expiration from the cookies list.
        - Searches for a specific cookie name and returns its value and expiry time.

    ### Args:
        - `cookies`: list[dict]
            A list of cookie dictionaries to search for the token.

    ### Returns:
        - `search_token`: str
            The value of the search token.
        - `expires`: int
            The expiration time of the token.
    """

    print("Extracting Auth Cookie")
    for i in cookies:
        if i["name"] == "UniversalSearchNuxt_vt":
            return i["value"]


def cookie_handler() -> tuple[str, list[dict]]:
    """
    ### Description:
        - Fetches an authentication token with retry logic.
        - Calls the get_cookies and extract_search_token functions.

    ### Returns:
        - `search_token`: str
            The retrieved search token.
        - `expires`: int
            The expiration time of the token.

    ### Raises:
        - `ValueError`:
            If no token is found after retries.
    """

    print("Fetching a token")
    retries = 0
    while retries < 3:
        try:
            cookies = get_cookies()
            search_token = extract_search_token(cookies)
            if not search_token:
                raise ValueError("No token found. Might try again")
            return search_token, cookies
        except Exception as e:
            print("Error fetching a token", type(e).__name__, e)
            retries += 1


def publish_token(token: str, cookies: list[dict]):
    """
    ### Description:
        - Publishes the retrieved token to a specified URL.
        - Sends a POST request with the token details to an API endpoint.

    ### Args:
        - `token`: tuple[str, int]
            A tuple containing the token value and its expiration time.

    """

    print("Publishing token")
    base_url = os.getenv("POSTGREST_URL")
    anon_key = os.getenv("SUPABASE_CLIENT_ANON_KEY")

    url = base_url + "token_tracker"

    payload = {
        "token_name": "UniversalSearch",
        "token_value": token,
        "cookies": cookies,
    }
    headers = {
        "apikey": anon_key,
        "Authorization": "Bearer " + anon_key,
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

    response = httpx.post(url, json=payload, headers=headers)
    print(response.status_code)
    print(response.text)


def validate_request(event: dict | str):
    """
    ### Description:
        - Validates the incoming request using a secret.
        - Handles both string and dictionary events to check the authentication secret.

    ### Args:
        - `event`: dict | str
            The event data containing a secret to validate.

    ### Returns:
        - `bool`
            Returns True if the validation is successful.

    ### Raises:
        - `RuntimeError`:
            If authentication fails due to mismatched secrets.
    """

    if isinstance(event, str):
        event = json.loads(event)

    request_secret = event.get("secret") or json.loads(event.get("body")).get("secret")
    if request_secret == os.getenv("AUTH_SECRET"):
        return True

    raise RuntimeError("Authentication failed")


def lambda_handler(event: dict, context):
    """
    ### Description:
        - Entry point for AWS Lambda function.
        - Validates the request and retrieves, then publishes the token.

    ### Args:
        - `event`: dict
            The event data containing the authentication secret.
        - `context`: any
            The context provided by AWS Lambda (not used here).

    ### Returns:
        - `str`
            A JSON string containing status code and the token.

    ### Raises:
        - `ValueError`:
            If no token is found after processing.
    """
    validate_request(event)
    token, cookies = cookie_handler()
    if not token:
        raise ValueError("No token found")
    print("Token retrived sucessfully")

    publish_token(token, cookies)

    print("All good. Returning token to invoker")
    return json.dumps({"status_code": 200, "token": token, "cookies": cookies})


if __name__ == "__main__":
    data = lambda_handler({"secret": os.getenv("AUTH_SECRET")}, {})
    print(data)
