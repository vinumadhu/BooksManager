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
            }, status=400)
        book = models.Book.objects.create(name=name, isbn=isbn, country=country, number_of_pages=number_of_pages,
                                          publisher=publisher, release_date=release_date)
        for author in authors:
            models.Author.objects.create(book=book, name=author)
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
        }, status=201)

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
    def patch(self, request, book_id):
        try:
            book = models.Book.objects.get(id=book_id)
        except models.Book.DoesNotExist:
            return JsonResponse({
                "status_code": 404,
                "status": "failed",
                "message": "Book does not exist"
            }, status=404)

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
            for author in params['authors']:
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

    def delete(self, request, book_id):
        try:
            book = models.Book.objects.get(id=book_id)
        except models.Book.DoesNotExist:
            return JsonResponse({
                "status_code": 404,
                "status": "failed",
                "message": "Book does not exist"
            }, status=404)
        name = book.name
        book.delete()
        return JsonResponse({
            "status_code": 200,
            "status": "success",
            "message": "The book " + name + " was deleted successfully",
            "data": []
        })

    def get(self, request, book_id):
        try:
            book = models.Book.objects.get(id=book_id)
        except models.Book.DoesNotExist:
            return JsonResponse({
                "status_code": 404,
                "status": "failed",
                "message": "Book does not exist"
            }, status=404)
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
        name = request.GET['name']
    except KeyError:
        return JsonResponse({
            "status_code": 400,
            "status": "failed"
        }, status=400)
    url = "https://www.anapioficeandfire.com/api/books"
    book_list = requests.get(url, params={'name': name}).json()
    data = []
    for book in book_list:
        data.append({
            "name": book.get('name'),
            "isbn": book.get('isbn'),
            "authors": book.get('authors'),
            "number_of_pages": book.get('number_of_pages'),
            "publisher": book.get('publisher'),
            "country": book.get('country'),
            "release_date": book.get('release_date')
        })
    return JsonResponse({
        "status_code": 200,
        "status": "success",
        "data": data
    })

