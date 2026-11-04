"""네트워크 없이 실행되는 Open Library 검색 처리 테스트."""

import io
import json
import unittest
from unittest.mock import patch

from api_books import search_books


class _Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()


class TestBookSearch(unittest.TestCase):
    @patch("api_books.urlopen")
    def test_book_data(self, mocked):
        document = {"docs": [{
            "title": "Python Programming",
            "author_name": ["Alice", "Bob"],
            "first_publish_year": 2022,
            "key": "/works/OL123W",
        }]}
        mocked.return_value = _Response(json.dumps(document).encode())
        result = search_books(" Python ")
        self.assertEqual(result[0]["title"], "Python Programming")
        self.assertEqual(result[0]["author"], "Alice, Bob")
        self.assertEqual(result[0]["year"], "2022")
        self.assertEqual(result[0]["url"], "https://openlibrary.org/works/OL123W")
        self.assertIn("q=Python", mocked.call_args.args[0].full_url)

    def test_blank_query(self):
        with self.assertRaises(ValueError):
            search_books("   ")

    @patch("api_books.urlopen")
    def test_no_results(self, mocked):
        mocked.return_value = _Response(b'{"docs": []}')
        self.assertEqual(search_books("unknown"), [])

    @patch("api_books.urlopen")
    def test_invalid_response(self, mocked):
        mocked.return_value = _Response(b'{"error": "bad response"}')
        with self.assertRaises(ValueError):
            search_books("Python")


if __name__ == "__main__":
    unittest.main()
