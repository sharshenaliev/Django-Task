from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal


class MyUser(AbstractUser):
    favorite = models.ManyToManyField('Book', verbose_name='Избранные книги')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Genre(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название жанра')

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя автора')

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'

    def __str__(self):
        return self.name


class Review(models.Model):
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE, verbose_name='Автор отзыва')
    rating = models.DecimalField(max_digits=3, decimal_places=1, verbose_name='Рейтинг',
                                 validators=[MaxValueValidator(Decimal(10.0)), MinValueValidator(Decimal(0.0))])
    text = models.TextField(verbose_name='Текст отзыва')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return self.text


class Book(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    slug = models.SlugField(max_length=100, unique=True, db_index=True, verbose_name="URL")
    description = models.TextField(verbose_name='Описание')
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT, verbose_name='Жанр')
    author = models.ForeignKey(Author, on_delete=models.PROTECT, verbose_name='Автор')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    reviews = models.ManyToManyField(Review, verbose_name='Список отзывов')


    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'

    def __str__(self):
        return self.name


