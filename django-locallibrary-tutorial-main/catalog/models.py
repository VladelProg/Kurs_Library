from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

from django.urls import reverse  # To generate URLS by reversing URL patterns
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from decimal import Decimal
import os
from django.conf import settings


class UserActionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)  # Описание действия
    timestamp = models.DateTimeField(default=timezone.now)  # Время действия

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"
    
    #def save(self, *args, **kwargs):
    #    super().save(*args, **kwargs) # Правильно: *args здесь используется для передачи аргументов
    #    log_user_action(self.user, self.action)


def log_user_action(user, action):
    """Записывает действия пользователя в текстовый файл."""

    # Получаем путь к файлу логов из настроек Django
    log_file_path = os.path.join(settings.BASE_DIR, 'logs', 'user_actions.txt')

    # Создаем директорию для логов, если ее нет
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    # Открываем файл в режиме добавления (a)
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"{timezone.now()} - {user.username} - {action}\n")

class Genre(models.Model):
    """Модель жанра книги"""
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Введите жанр книги (Например, научная фантастика, зарубежная поэзия)"
    )

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a particular genre instance."""
        return reverse('genre-detail', args=[str(self.id)])

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='genre_name_case_insensitive_unique',
                violation_error_message = "Жанр уже существуeт (case insensitive match)"
            ),
        ]

class Language(models.Model):
    name = models.CharField(max_length=200,
                            unique=True,
                            help_text="Введите язык, на котором написана книга (например, Английский)")

    def get_absolute_url(self):
        """Returns the url to access a particular language instance."""
        return reverse('language-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='language_name_case_insensitive_unique',
                violation_error_message = "Язык уже есть в базе"
            ),
        ]

class Book(models.Model):
    """Модель книги (только в базе, не на руках)."""
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.RESTRICT, null=True)
    path_to_icon = models.CharField(max_length=200, help_text="Введите путь к изображению")
    path_to_file = models.CharField(max_length=255)
    rating = models.IntegerField(null=True, blank=True)   # Добавляем поле для рейтинга (по сути заглушка)
    # Foreign Key used because book can only have one author, but authors can have multiple books.
    # Author as a string rather than object because it hasn't been declared yet in file.
    summary = models.TextField(
        max_length=1000, help_text="Введите описание книги")
    isbn = models.CharField('ISBN', max_length=13,
                            unique=True,
                            help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn'
                                      '">ISBN number</a>')
    genre = models.ManyToManyField(
        Genre, help_text="Выберите жанр книги")
    # ManyToManyField used because a genre can contain many books and a Book can cover many genres.
    # Genre class has already been defined so we can specify the object above.
    language = models.ForeignKey(
        'Language', on_delete=models.SET_NULL, null=True)
    #models.ImageField

    class Meta:
        ordering = ['title', 'author']

    def get_average_rating(self):
        ratings = self.ratings.all()  # Связь с моделью Rating
        if ratings.exists():
            return sum([rating.value for rating in ratings]) / ratings.count()
        return 0
    
    def display_genre(self):
        """Creates a string for the Genre. This is required to display genre in Admin."""
        return ', '.join([genre.name for genre in self.genre.all()[:3]])
    
    def display_icon(self):
        return self.path_to_icon
    
    def display_file(self):
        return self.path_to_file
    
    display_genre.short_description = 'Genre'

    def get_absolute_url(self):
        """Returns the url to access a particular book record."""
        return reverse('book-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return self.title
    
#class Rating(models.Model):
#    user = models.ForeignKey(User, on_delete=models.CASCADE)
#    book = models.ForeignKey(Book, related_name='ratings', on_delete=models.CASCADE)
#    value = models.IntegerField()  # Оценка, например от 1 до 5

#    class Meta:
#        unique_together = ('user', 'book')  # Один пользователь может оставить одну оценку для каждой книги



import uuid  # Required for unique book instances
from datetime import date

from django.conf import settings  # Required to assign User as a borrower


class BookInstance(models.Model):
    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this particular book across whole library")
    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def is_overdue(self):
        """Determines if the book is overdue based on due date and current date."""
        return bool(self.due_back and date.today() > self.due_back)

    LOAN_STATUS = (
        ('d', 'Обслуживание'),
        ('o', 'На дому'),
        ('a', 'Свободна'),
        ('r', 'Зарезервирована'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='d',
        help_text='Статус')

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    def get_absolute_url(self):
        """Returns the url to access a particular book instance."""
        return reverse('bookinstance-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id} ({self.book.title})'


class Author(models.Model):
    """Модель автора книги."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.last_name}, {self.first_name}'