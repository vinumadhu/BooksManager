import requests
import json

from django.http import JsonResponse
from django.views import View
from . import models


class BooksCreateRead(View):
    def post(self, request):
        try:
            params = json.loads(request.body)
            name = params["name"]
            isbn = params["isbn"]
            authors = params["authors"]
            country = params["country"]
            number_of_pages = params["number_of_pages"]
            publisher = params["publisher"]
            release_date = params["release_date"]
        except KeyError:
            return JsonResponse({
                "status_code": 400,
                "status": "Failed"
            })
        book = models.Book(name=name, isbn=isbn, country=country, number_of_pages=number_of_pages,
                           publisher=publisher, release_date=release_date)
        book.save()
        for author in authors:
            models.Author(book=book, name=author).save()
        return JsonResponse({
            "status_code": 201,
            "status": "success",
            "data": [
                {"book": {
                    "name": name,
                    "isbn": isbn,
                    "authors": authors,
                    "number_of_pages": number_of_pages,
                    "publisher": publisher,
                    "country": country,
                    "release_date": release_date
                }}
            ]
        })

    def get(self, request):
        filtered_books = models.Book.objects.all()
        if 'name' in request.GET:
            filtered_books = filtered_books.filter(name=request.GET['name'])
        if 'publisher' in request.GET:
            filtered_books = filtered_books.filter(publisher=request.GET['publisher'])
        if 'country' in request.GET:
            filtered_books = filtered_books.filter(country=request.GET['country'])
        if 'release_date' in request.GET:
            filtered_books = filtered_books.filter(release_date=request.GET['release_date'])
        books_details = []
        if not filtered_books:
            return JsonResponse({
                "status_code": 200,
                "status": "success",
                "data": []
            })
        for book in filtered_books:
            books_details.append({
                "id": book.id,
                "name": book.name,
                "isbn": book.isbn,
                "authors": list(book.author_set.all().values_list('name', flat=True)),
                "number_of_pages": book.number_of_pages,
                "publisher": book.publisher,
                "country": book.country,
                "release_date": book.release_date
            })
        return JsonResponse({
            "status_code": 200,
            "status": "success",
            "data": books_details
        })


class BooksUpdateDeleteFetch(View):
    def patch(self, request):
        try:
            book_id = self.kwargs['book_id']
        except KeyError:
            return JsonResponse({
                "status_code": 400,
                "status": "failed"
            })
        try:
            book = models.Book.objects.get(id=book_id)
        except models.Book.DoesNotExist:
            return JsonResponse({
                "status_code": 404,
                "status": "failed",
                "message": "Book does not exist"
            })

        params = json.loads(request.body)
        if 'name' in params:
            book.name = params['name']
        if 'isbn' in params:
            book.isbn = params['isbn']
        if 'country' in params:
            book.country = params['country']
        if 'number_of_pages' in params:
            book.number_of_pages = params['number_of_pages']
        if 'publisher' in params:
            book.publisher = params['publisher']
        if 'release_date' in params:
            book.release_date = params['release_date']
        book.save()

        if 'authors' in params:
            models.Author.objects.filter(book=book).delete()
            for author in params['author']:
                models.Author(book=book, name=author).save()
        return JsonResponse({
            "status_code": 200,
            "status": "success",
            "message": "The book " + book.name + " was updated successfully",
            "data": {
                "id": book.id,
                "name": book.name,
                "isbn": book.isbn,
                "authors": list(book.author_set.all().values_list('name', flat=True)),
                "number_of_pages": book.number_of_pages,
                "publisher": book.publisher,
                "country": book.country,
                "release_date": book.release_date
            }
        })

    def delete(self, request):
        try:
            book_id = self.kwargs['book_id']
        except KeyError:
            return JsonResponse({
                "status_code": 400,
                "status": "failed"
            })
        try:
            book = models.Book.objects.get(id=book_id)
        except models.Book.DoesNotExist:
            return JsonResponse({
                "status_code": 404,
                "status": "failed",
                "message": "Book does not exist"
            })
        name = book.name
        book.delete()
        return JsonResponse({
            "status_code": 200,
            "status": "success",
            "message": "The book " + name + " was deleted successfully",
            "data": []
        })

    def get(self, request):
        try:
            book_id = self.kwargs['book_id']
        except KeyError:
            return JsonResponse({
                "status_code": 400,
                "status": "failed"
            })
        try:
            book = models.Book.objects.get(id=book_id)
        except models.Book.DoesNotExist:
            return JsonResponse({
                "status_code": 404,
                "status": "failed",
                "message": "Book does not exist"
            })
        return JsonResponse({
            "status_code": 200,
            "status": "success",
            "data": {
                "id": book.id,
                "name": book.name,
                "isbn": book.isbn,
                "authors":  list(book.author_set.all().values_list('name', flat=True)),
                "number_of_pages": book.number_of_pages,
                "publisher": book.publisher,
                "country": book.country,
                "release_date": book.release_date
            }
        })


def get_external_books(request):
    try:
        name = request.GET.get('name')
    except KeyError:
        return JsonResponse({
            "status_code": 400,
            "status": "failed"
        })
    url = "https://www.anapioficeandfire.com/api/books"
    response = requests.get(url, params={'name': name})
    book_list = json.loads(response)
    data = []
    for book in book_list:
        data.append({
            "name": book.name,
            "isbn": book.isbn,
            "authors": book.authors,
            "number_of_pages": book.number_of_pages,
            "publisher": book.publisher,
            "country": book.country,
            "release_date": book.release_date
        })
    return JsonResponse({
        "status_code": 200,
        "status": "success",
        "data": data
    })

