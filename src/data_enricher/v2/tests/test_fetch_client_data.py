"""Tests for fetch client data"""

import json
import os
from unittest import TestCase, main
from unittest.mock import Mock, patch

import httpx
from dotenv import load_dotenv
from wrapworks import cwdtoenv

load_dotenv()
cwdtoenv()

from v2.src.fetch_client_data import lambda_handler


class TestLambdaHandler(TestCase):

    def get_pending_rows(self) -> list[str] | None:
        """sideeffect to get pending rows"""

        url = os.getenv("POSTGREST_URL") + "upwork_filtered_jobs"

        params = {
            "did_augment_client_data": "eq.true",
            "select": "link",
            "limit": 5,
            "order": "published_date.desc",
        }

        headers = {
            "apikey": os.getenv("SUPABASE_CLIENT_ANON_KEY"),
            "Authorization": f"Bearer {os.getenv('SUPABASE_CLIENT_ANON_KEY')}",
            "Content-Type": "application/json",
        }

        response = httpx.get(url, headers=headers, params=params)

        rows = response.json()
        if not rows:
            return None
        return [x["link"] for x in rows]

    def setUp(self) -> None:
        pass

    @patch("v2.src.fetch_client_data.get_pending_rows")
    def test_good_return(self, mock_get_rows: Mock):
        """Basic test to check if rows get processed successfully"""

        mock_get_rows.side_effect = self.get_pending_rows

        res = lambda_handler({}, {})

        self.assertEqual(json.loads(res)["status"], "Rows processed successfully")


if __name__ == "__main__":
    main()
