from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
# Create your views here.

from .models import Book, Author, BookInstance, Genre, Language, Rating, logs
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
    

#import logging

#logger = logging.getLogger('main')

def index(request):
    """Информация о сайте"""
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Available copies of books
    num_instances_available = BookInstance.objects.filter(
        status__exact='a').count()
    num_authors = Author.objects.count()  # The 'all()' is implied by default.

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    # Render the HTML template index.html with the data in the context variable.
    return render(
        request,
        'index.html',
        context={'num_books': num_books, 'num_instances': num_instances,
                 'num_instances_available': num_instances_available, 'num_authors': num_authors,
                 'num_visits': num_visits},
    )
    
from django.http import JsonResponse
from decimal import Decimal


def book_detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)

    # Проверяем средний рейтинг
    average_rating_data = book.ratings.aggregate(average_rating=Avg('rating'))
    print(f"Средний рейтинг для книги {book.title}: {average_rating_data['average_rating']}")

    context = {
        'book': book,
        'average_rating': average_rating_data['average_rating'],
    }
    return render(request, 'catalog/book_detail.html', context)

from django.core.paginator import Paginator

def book_list(request):
    book_list = Book.objects.all()  # Получаем все книги

    # Сортировка по заголовку (опционально)
    sort_by = request.GET.get('sort', '')
    if sort_by:
        book_list = book_list.order_by(sort_by)

    paginator = Paginator(book_list, 4)  # Убедимся, что 5 книг на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'catalog/book_list.html', context)


def add_rating(request, book_id):
    book = get_object_or_404(Book, pk=book_id)

    if request.method == 'POST':
        rating = request.POST.get('rating')

        if rating:
            try:
                rating = int(rating)
                if 0 <= rating <= 5:
                    # Обновляем сумму рейтингов и количество голосов
                    book.rating += rating
                    #book.rating_count += 1
                    book.save()

                    return redirect('book_detail', book_id=book_id)
                else:
                    return JsonResponse({'success': False, 'message': 'Рейтинг должен быть от 0 до 5.'})
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Введите корректный рейтинг.'})
        else:
            return JsonResponse({'success': False, 'message': 'Пожалуйста, введите рейтинг.'})

    return render(request, 'catalog/book_detail.html', {'book': book})


from django.views import generic
   

class BookListView(generic.ListView):
    """Коллекция книг."""
    #logger.info('Заход на страницу Просмотр коллекции книг')
    model = Book
    paginate_by = 2 # Выводим по 5 книг на страницу
    template_name = 'book_list.html'
    context_object_name = 'book_list'

    def get_queryset(self):
        sort = self.request.GET.get('sort', 'title') # Получаем параметр сортировки
        queryset = Book.objects.all().order_by(sort) # Сортируем книги
        return queryset
    
class BookListUserView(generic.ListView):
    """Коллекция книг."""
    #logger.info('Заход на страницу Просмотр коллекции книг')
    model = Book
    paginate_by = 2 # Выводим по 5 книг на страницу
    #template_name = 'insex_user.html'
    #context_object_name = 'book_list_user'

    def get_queryset(self):
        sort = self.request.GET.get('sort', 'title') # Получаем параметр сортировки
        queryset = Book.objects.all().order_by(sort) # Сортируем книги
        return queryset
    
class BookDetailView(generic.DetailView):
    model = Book
       
    def get_object(self):
        book = super().get_object()
        #logger.info(f'Заход на страницу Просмотр информации о книге {book.title}')
        return book


class AuthorListView(generic.ListView):
    """Generic class-based list view for a list of authors."""
    model = Author
    paginate_by = 2
    template_name = 'author_list.html'
    context_object_name = 'author_list'
    #logger.info('Заход на страницу Просмотр списках авторов')
    def get_queryset(self):
        sort = self.request.GET.get('sort', 'last_name')  # Получаем параметр сортировки
        return Author.objects.all().order_by(sort)  # Сортировка по выбранному элементу

def action_logs_view(request):
    if request.user.is_authenticated:
        logs.objects.create(
            user=request.user,
            action="Visited home page",
            timestamp=datetime.datetime.now()
    )
    logss = logs.objects.all()  # Получаем все записи из таблицы логов
    return render(request, 'index_user.html', {'logs': logss})



class AdminShowData(generic.ListView):
    model = logs
    paginate_by = 20 # Выводим по 5 книг на страницу
    template_name = 'catalog/index_user.html'
    context_object_name = 'index_user'
    def get_queryset(self):
        sort = self.request.GET.get('sort', 'action')  # Получаем параметр сортировки
        return logs.objects.all().order_by(sort)

def user_logs_view(request):
    logs_list = logs.objects.all().order_by('-timestamp')  # Сортировка по дате
    paginator = Paginator(logs_list, 10)  # Показывать по 10 логов на странице

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'catalog/index_user.html', {'page_obj': page_obj, 'logs': page_obj})

def some_view(request):
    # Ваш код обработки действий пользователя
    logs.objects.create(user=request.user, action="Visited the page", timestamp=datetime.datetime.now())
    return render(request, 'catalog/book_list.html')

class AuthorDetailView(generic.DetailView):
    """Generic class-based detail view for an author."""
    
    model = Author
       
    def get_object(self):
        author = super().get_object()
        #logger.info(f'Заход на страницу Просмотр информации о авторе {author.first_name} {author.last_name}')
        return author

class GenreDetailView(generic.DetailView):
    """Generic class-based detail view for a genre."""
    model = Genre
    
    def get_object(self):
        genre = super().get_object()
        #logger.info(f'Заход на страницу Просмотр информации о жанре {genre.name}')
        return genre

class GenreListView(generic.ListView):
    """Generic class-based list view for a list of genres."""
    model = Genre
    paginate_by = 10

class LanguageDetailView(generic.DetailView):
    """Generic class-based detail view for a genre."""
    model = Language
    
    def get_object(self):
        language = super().get_object()
        #logger.info(f'Заход на страницу Просмотр книг на языке {language.name}')
        return language

class LanguageListView(generic.ListView):
    """Generic class-based list view for a list of genres."""
    model = Language
    paginate_by = 10

class BookInstanceListView(generic.ListView):
    """Generic class-based view for a list of books."""
    model = BookInstance
    paginate_by = 10

class BookInstanceDetailView(generic.DetailView):
    """Generic class-based detail view for a book."""
    model = BookInstance

from django.contrib.auth.mixins import LoginRequiredMixin

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )

# Added as part of challenge!
from django.contrib.auth.mixins import PermissionRequiredMixin


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from django.contrib.auth.decorators import login_required, permission_required
from catalog.forms import RenewBookForm


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/11/2023'}
    permission_required = 'catalog.add_author'
    
    #logger.info('Добавление автора в базу')

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    # Not recommended (potential security issue if more fields added)
    fields = '__all__'
    permission_required = 'catalog.change_author'
    
    def get_object(self):
        author = super().get_object()
        #logger.info(f'Обновление информации об авторе {author.name}')
        return author

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.delete_author'

    def get_object(self):
        author = super().get_object()
        #logger.info(f'Удаление автора {author.name}')
        return author
    
    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("author-delete", kwargs={"pk": self.object.pk})
            )

# Classes created for the forms challenge

class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'catalog.add_book'
    
    #logger.info('Создание новой книги')


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language', 'path_to_icon']
    permission_required = 'catalog.change_book'
    
    def get_object(self):
        book = super().get_object()
        #logger.info(f'Обновление информации о книге {book.title}')
        return book

def book_list_view(request):
    sort = request.GET.get('sort', 'asc')  # Получаем параметр сортировки, по умолчанию сортировка по возрастанию
    if sort == 'desc':
        books = Book.objects.all().order_by('-title')  # Сортировка по убыванию
    else:
        books = Book.objects.all().order_by('title')   # Сортировка по возрастанию
    return render(request, 'book_list.html', {'book_list': books})

class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.delete_book'

    def get_object(self):
        book = super().get_object()
        #logger.info(f'Удаление книги {book.title}')
        return book
    
    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("book-delete", kwargs={"pk": self.object.pk})
            )


class GenreCreate(PermissionRequiredMixin, CreateView):
    model = Genre
    fields = ['name', ]
    permission_required = 'catalog.add_genre'
    
    #logger.info('Создание нового жанра')


class GenreUpdate(PermissionRequiredMixin, UpdateView):
    model = Genre
    fields = ['name', ]
    permission_required = 'catalog.change_genre'

    def get_object(self):
        genre = super().get_object()
        #logger.info(f'Обновление информации о жанре {genre.name}')
        return genre

class GenreDelete(PermissionRequiredMixin, DeleteView):
    model = Genre
    success_url = reverse_lazy('genres')
    permission_required = 'catalog.delete_genre'

    def get_object(self):
        genre = super().get_object()
        #logger.info(f'Удаление жанра {genre.name}')
        return genre

class LanguageCreate(PermissionRequiredMixin, CreateView):
    model = Language
    fields = ['name', ]
    permission_required = 'catalog.add_language'

    #logger.info('Создание нового языка')

class LanguageUpdate(PermissionRequiredMixin, UpdateView):
    model = Language
    fields = ['name', ]
    permission_required = 'catalog.change_language'

    def get_object(self):
        language = super().get_object()
        #logger.info(f'Обновление информации о языке {language.name}')
        return language

class LanguageDelete(PermissionRequiredMixin, DeleteView):
    model = Language
    success_url = reverse_lazy('languages')
    permission_required = 'catalog.delete_language'

    def get_object(self):
        language = super().get_object()
        #logger.info(f'Удаление языка {language.name}')
        return language

class BookInstanceCreate(PermissionRequiredMixin, CreateView):
    model = BookInstance
    fields = ['book', 'imprint', 'due_back', 'borrower', 'status']
    permission_required = 'catalog.add_bookinstance'


class BookInstanceUpdate(PermissionRequiredMixin, UpdateView):
    model = BookInstance
    # fields = "__all__"
    fields = ['imprint', 'due_back', 'borrower', 'status']
    permission_required = 'catalog.change_bookinstance'


class BookInstanceDelete(PermissionRequiredMixin, DeleteView):
    model = BookInstance
    success_url = reverse_lazy('bookinstances')
    permission_required = 'catalog.delete_bookinstance'
