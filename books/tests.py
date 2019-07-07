import json

from django.test import TestCase
from books.models import Book


class BookListingTest(TestCase):
    url = '/api/v1/books'
    @classmethod
    def setUpTestData(cls):
        for book_id in range(7):
            Book.objects.create(name="name" + str(book_id), isbn="isbn" + str(book_id),
                                country="country" + str(book_id), number_of_pages=book_id,
                                publisher="publisher" + str(book_id), release_date="release_date" + str(book_id))

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_lists_all_books(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json().get('data')), 7)

    def test_list_filtered_books(self):
        params = {
            'name': 'name0',
            'publisher': 'publisher0',
            'country': 'country0',
            'release_date': 'release_date0',
        }
        response = self.client.get(self.url, params)
        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(result.get('data')), 1)
        response = self.client.get(self.url, {'name': 'Name'})
        result = response.json()
        self.assertEqual(len(result.get('data')), 0)


class TestBookCreate(TestCase):
    url = '/api/v1/books'

    def test_create_book(self):
        data = {
            "name": "name",
            "isbn": "1123",
            "authors": ["authors0", "authors1", "authors2", "authors3", "authors4", "authors5"],
            "country": "country",
            "number_of_pages": 24,
            "publisher": "publisher",
            "release_date": "release_date"
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        book_count = Book.objects.filter(isbn='1123').count()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(book_count, 1)

    def test_create_book_error(self):
        data = {
            "name": "name",
            "isbn": "1123",
            "authors": ["authors0", "authors1", "authors2", "authors3", "authors4", "authors5"],
            "country": "country",
            "number_of_pages": 24,
            "publisher": "publisher"
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)


class BookUpdateDeleteFetchTest(TestCase):
    url = '/api/v1/books/'

    def setUp(self):
        Book.objects.create(name="name", isbn="isbn", country="country", number_of_pages=35,
                            publisher="publisher", release_date="release_date")

    def test_update_book(self):
        data = {
            "name": "new_name",
            "isbn": "new_isbn",
            "authors": ["authors0", "authors1", "authors2", "authors3", "authors4", "authors5"],
            "country": "new_country",
            "number_of_pages": 24,
            "publisher": "new_publisher",
            "release_date": "new_release_date"
        }
        response = self.client.patch(self.url + "1", json.dumps(data), content_type='application/json')
        updated_book = Book.objects.get(id=1)
        self.assertEqual(updated_book.name, "new_name")
        self.assertEqual(response.status_code, 200)

    def test_update_no_book_error(self):
        response = self.client.patch(self.url + "2")
        self.assertEqual(response.status_code, 404)

    def test_delete_book(self):
        response = self.client.delete(self.url + "1")
        book_count = Book.objects.filter(id=1).count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(book_count, 0)

    def test_delete_no_book_error(self):
        response = self.client.delete(self.url + "2")
        self.assertEqual(response.status_code, 404)

    def test_fetch_book(self):
        response = self.client.get(self.url + "1")
        data = response.json().get('data')
        self.assertEqual(data.get('name'), "name")

    def test_fetch_book_error(self):
        response = self.client.get(self.url + "2")
        self.assertEqual(response.status_code, 404)


class ExternalBookTest(TestCase):
    url = '/api/external-books'

    def test_external_book(self):
        response = self.client.get(self.url, {'name': 'A Game of Thrones'})
        self.assertEqual(response.status_code, 200)

    def test_external_book_no_book(self):
        response = self.client.get(self.url, {'name': 'Random no name'})
        self.assertEqual(response.status_code, 200)

    def test_external_book_error(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)

