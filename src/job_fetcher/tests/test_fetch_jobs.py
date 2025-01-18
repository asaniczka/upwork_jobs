"""Intergration test for fetch jobs"""

# pylint: disable=wrong-import-position

from unittest import TestCase, main

from wrapworks import cwdtoenv
from dotenv import load_dotenv

cwdtoenv()
load_dotenv()

from src.fetch_jobs import lambda_handler


class TestCollectJobs(TestCase):

    def test_collect_jobs_status_code(self):
        """Test that collect_jobs returns status code 200."""

        response = lambda_handler({}, {})
        self.assertEqual(response["statusCode"], 200)


# Run the tests
if __name__ == "__main__":
    main()
