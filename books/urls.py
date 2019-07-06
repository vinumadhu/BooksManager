from django.urls import path
from .views import BooksCreateRead, BooksUpdateDeleteFetch, get_external_books

urlpatterns = [
    path('v1/books', BooksCreateRead.as_view()),
    path('v1/books/<int:book_id>', BooksUpdateDeleteFetch.as_view()),
    path('external-books', get_external_books, name='external-books')
]