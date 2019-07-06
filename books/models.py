from django.db import models


class Book(models.Model):
    name = models.CharField(max_length=50)
    isbn = models.CharField(max_length=50)
    number_of_pages = models.IntegerField()
    publisher = models.CharField(max_length=50)
    release_date = models.CharField(max_length=50)
    country = models.CharField(max_length=50)


class Author(models.Model):
    name = models.CharField(max_length=50)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

