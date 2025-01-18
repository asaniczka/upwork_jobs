"""Tests for proper token retrival"""

# pylint:disable=wrong-import-position

from unittest import TestCase, main
import os
import json

from wrapworks import cwdtoenv
from dotenv import load_dotenv

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
