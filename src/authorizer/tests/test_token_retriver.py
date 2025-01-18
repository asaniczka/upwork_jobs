"""Tests for proper token retrival"""

# pylint:disable=wrong-import-position

import json
import os
from unittest import TestCase, main

from dotenv import load_dotenv
from wrapworks import cwdtoenv

load_dotenv()
cwdtoenv()

from src.token_retriver import lambda_handler


class TestGetToken(TestCase):

    def test_get_token(self):

        res = lambda_handler({"secret": os.getenv("AUTH_SECRET")}, {})

        data = json.loads(res)
        self.assertEqual(data["status_code"], 200)
        self.assertTrue("oauth2v2" in data["token"])


if __name__ == "__main__":
    main()
