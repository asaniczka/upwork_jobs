"""
### Description:
    - This module contains the worker responsible for 
      gathering client data from Upwork job postings.
"""

# pylint:disable=wrong-import-position

import os

import chompjs
import httpx
from dotenv import load_dotenv
from pydantic import ValidationError
from rich import print
from wrapworks import cwdtoenv

cwdtoenv()
load_dotenv()

from src.models.genai_models import (
    LLM_COST_PER_TOKEN,
    AIResponse,
    LLMMessage,
    LLMMessageLog,
    LLMRoles,
    ValidLLMModels,
)
from src.models.upwork_models import OPENAPI_SCHEMA, PostingAttributes
from src.upwork_accounts.browser_handlers import get_page

# ----------------------------------------
#               WORKERS
# ----------------------------------------


def invoke_openai(model: ValidLLMModels | str, messages: LLMMessageLog) -> AIResponse:
    """
    ### Description:
        - Invokes the OpenAI API to generate a chat completion
          based on provided messages and model.

    ### Args:
        - `model`: ValidLLMModels | str
            The model to be used for the API call.
        - `messages`: LLMMessageLog
            The logged messages to be sent in the request.

    ### Returns:
        - `AIResponse`
            The response from the OpenAI API containing the
            generated output.

    ### Raises:
        - `RuntimeError`:
            If there is an error during the API call or response parsing.
    """

    if not isinstance(model, str):
        model = model.value

    url = "https://api.openai.com/v1/chat/completions"

    payload = {
        "model": model,
        "messages": [x.model_dump() for x in messages.messages],
        "max_tokens": 3000,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('AZ_OPENAI_API_KEY')}",
    }

    with httpx.Client() as client:
        response = client.post(url, json=payload, headers=headers, timeout=120)

    try:
        data = response.json()
        if data.get("error"):
            print(payload)
            raise RuntimeError(data["error"]["message"])
        return AIResponse(**data)
    except RuntimeError:
        raise
    except Exception as e:
        print(f"Error parsing {response.text}: {type(e).__name__}: {e}")
        raise


def handler_generate_response(
    messages: LLMMessageLog, model: ValidLLMModels
) -> AIResponse:
    """
    ### Description:
        - Generates a response from the OpenAI model based
          on the provided messages.

    ### Args:
        - `messages`: LLMMessageLog
            The logged messages to generate a response for.
        - `model`: ValidLLMModels
            The model to be used for the generation.

    ### Returns:
        - `AIResponse`
            The generated response from the OpenAI model.
    """

    response = invoke_openai(model, messages)
    response.calculate_cost(model.value, LLM_COST_PER_TOKEN)

    return response


def convert_response_to_schema(res: str) -> PostingAttributes:
    """
    ### Description:
        - Converts a string response from the OpenAI API into
          a structured PostingAttributes object.

    ### Args:
        - `res`: str
            The JSON response string from the OpenAI API.

    ### Returns:
        - `PostingAttributes`
            A structured object containing job posting attributes.

    ### Raises:
        - `ValidationError`:
            If the response does not conform to the PostingAttributes schema.
    """

    data = chompjs.parse_js_object(res)
    schemed_product = PostingAttributes(**data)
    return schemed_product


def entry_extract_attributes(page: str) -> tuple[AIResponse, PostingAttributes]:
    """
    ### Description:
        - Extracts job posting attributes from a webpage using
          the OpenAI API to parse the content.

    ### Args:
        - `page`: str
            The content of the webpage to extract attributes from.

    ### Returns:
        - `tuple[AIResponse, PostingAttributes]`
            A tuple containing the generated AI response and the
            parsed posting attributes.
    """

    print("Extracting attributes from a page")

    messages = LLMMessageLog(
        messages=[
            LLMMessage(
                role=LLMRoles.SYSTEM,
                content="""You are a upwork job parser. User will provide you with the getTExt of a webpage. 
                Extract all the data to match the schema. Job description must be the full description. Don't truncate.
                Reply in valid JSON.
                """,
            ),
            LLMMessage(
                role=LLMRoles.SYSTEM,
                content=f"""Below is the OpenAPI JSON schema:

                {OPENAPI_SCHEMA}
                """,
            ),
        ]
    )

    messages.messages.append(LLMMessage(role=LLMRoles.USER, content=page))

    running_cost = 0
    retries = 0
    while retries < 5:
        try:
            response = handler_generate_response(
                messages, ValidLLMModels.OPENAI_GPT4o_MINI
            )
            # add current cost to checkpoint incase validation fails
            if response:
                running_cost += response.cost

            parsed_job = convert_response_to_schema(response.text)
            response.cost = running_cost  # combine cost of failed previous runs
            return response, parsed_job
        except ValidationError:
            retries += 1
            print(f"Error extracting metadata with OpenAI. Retrying...")
        except Exception as e:
            retries += 1
            print(
                f"Error extracting metadata with OpenAI: {type(e).__name__}: {e}. Retrying..."
            )


if __name__ == "__main__":
    url = "https://www.upwork.com/jobs/Azure-Communication-Services-Expert_%7E01ca8dd0ca558e3386?source=rss"
    page = get_page(url)
    res = entry_extract_attributes(page)
    print(res)
