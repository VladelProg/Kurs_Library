from django.views.decorators.http import require_POST

from django.shortcuts import render, get_object_or_404, redirect

from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Avg
from django.views.generic import ListView
from django.views import generic, View

from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy

from django.views.generic.edit import CreateView, UpdateView, DeleteView

from catalog.forms import RenewBookForm

from .models import Book, Author, BookInstance, Genre, Language, Rating, logs
import datetime


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
    

@require_POST
def add_rating(request, book_id):
    try:
        book = get_object_or_404(Book, id=book_id)
        rating_value = int(request.POST.get('rating', 0))

        # Проверяем, что рейтинг в пределах 0-5
        if 0 <= rating_value <= 5:
            Rating.objects.create(book=book, user=request.user, rating=rating_value)
            average_rating = book.ratings.aggregate(Avg('rating'))['rating__avg']

            return JsonResponse({
                'message': 'Рейтинг успешно добавлен!',
                'average_rating': round(average_rating, 2),
            })
        else:
            return JsonResponse({'message': 'Рейтинг должен быть от 0 до 5.'}, status=400)

    except Exception as e:
        return JsonResponse({'message': 'Ошибка при добавлении рейтинга.'}, status=500)
 

class BookListView(generic.ListView):
    """Коллекция книг."""
    model = Book
    paginate_by = 2  # Выводим по 2 книги на страницу
    template_name = 'book/book_list.html'
    context_object_name = 'book_list'

    def get_queryset(self):
        queryset = Book.objects.all()
        
        # Добавляем сортировку, если она указана в запросе
        sort = self.request.GET.get('sort')
        if sort:
            queryset = queryset.order_by(sort)

        # Аннотируем средний рейтинг для каждой книги
        queryset = queryset.annotate(average_rating=Avg('ratings__rating')).order_by('-average_rating')
        
        return queryset


class AdminBookListView(generic.ListView):
    model = Book
    paginate_by = 6
    template_name = 'book/admin_book_list.html'
    context_object_name = 'book-list'

    def get_queryset(self):
        sort = self.request.GET.get('sort', 'title')  # Получаем параметр сортировки
        return Book.objects.all().order_by(sort)
    
class AdminBookDetailView(generic.DetailView):
    model = Book
    template_name = 'book/admin_book_detail.html'
    def get_object(self):
        book = super().get_object()
        return book

class BookDetailView(generic.DetailView):
    model = Book
    template_name = 'book/book_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем книгу и вычисляем средний рейтинг
        book = self.get_object()
        average_rating = Rating.objects.filter(book=book).aggregate(Avg('rating'))['rating__avg'] or 0
        context['average_rating'] = round(average_rating, 1)
        
        return context


class AuthorListView(generic.ListView):
    """Generic class-based list view for a list of authors."""
    model = Author
    paginate_by = 2
    template_name = 'author/author_list.html'
    context_object_name = 'author_list'
    def get_queryset(self):
        sort = self.request.GET.get('sort', 'last_name')  # Получаем параметр сортировки
        return Author.objects.all().order_by(sort)  

class AdminAuthorListView(generic.ListView):
    model = Author
    paginate_by = 2
    template_name = 'author/admin_author_list.html'  # Новый шаблон для админки
    context_object_name = 'admin_author_list'
    
    def get_queryset(self):
        sort = self.request.GET.get('sort', 'last_name')
        return Author.objects.all().order_by(sort)






class AdminLoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'admin_login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_superuser:
                login(request, user)
                return redirect('admin_panel')  # Перенаправляем на admin_panel.html
        return render(request, 'admin_login.html', {'form': form})

class AdminPanelView(LoginRequiredMixin, UserPassesTestMixin, View):
    # Этот метод определяет, является ли пользователь суперпользователем
    def test_func(self):
        return self.request.user.is_superuser

    # Если пользователь не прошел проверку, его перенаправят на страницу входа
    def handle_no_permission(self):
        return redirect('admin_login')  # Перенаправляем на страницу входа

    def get(self, request):
        # Здесь вы можете передать дополнительные контексты в шаблон, если это необходимо
        return render(request, 'admin_panel.html')
    

class AdminShowData(UserPassesTestMixin, ListView):
    model = logs
    paginate_by = 20
    template_name = 'catalog/log.html'
    context_object_name = 'log'

    def get_queryset(self):
        sort = self.request.GET.get('sort', 'timestamp')
        return logs.objects.all().order_by(sort)

    # Проверка, является ли пользователь суперпользователем
    def test_func(self):
        return self.request.user.is_superuser

    # Если пользователь не авторизован, перенаправить на страницу входа
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            # Если пользователь вошел, но не суперпользователь — отказ
            return redirect_to_login(self.request.get_full_path(), login_url=reverse_lazy('login'))
            #return HttpResponseForbidden("Недостаточно прав для просмотра данной страницы.")
        else:
            # Если пользователь не вошел — перенаправить на форму входа
            return redirect_to_login(self.request.get_full_path(), login_url=reverse_lazy('login'))


from django.db.models import Q
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView

class AdminShowData(UserPassesTestMixin, ListView):
    model = logs
    paginate_by = 10
    template_name = 'catalog/log.html'
    context_object_name = 'logs'

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect(reverse_lazy('login'))

    def get_queryset(self):
        queryset = logs.objects.all()
        username = self.request.GET.get('username', '')
        sort = self.request.GET.get('sort', 'timestamp')

        # Фильтрация по имени пользователя
        if username:
            queryset = queryset.filter(user__icontains=username)

        # Сортировка
        return queryset.order_by(sort)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.request.GET.get('username', '')
        context['sort'] = self.request.GET.get('sort', 'timestamp')
        return context
from django.core.paginator import Paginator
from django.shortcuts import render

def log_view(request):
    username = request.GET.get('user', '')  # Получаем значение из поля поиска
    logss = logs.objects.all()

    # Фильтрация по пользователю, если указано значение
    if username:
        logss = logss.filter(user__icontains=username)  # Фильтруем логи по имени пользователя

    paginator = Paginator(logss, 10)  # Пагинация по 10 записей
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'log.html', {'page_obj': page_obj, 'username': username})

def some_view(request):
    # Ваш код обработки действий пользователя
    logs.objects.create(user=request.user, action="Visited the page", timestamp=datetime.datetime.now())
    return render(request, 'catalog/book_list.html')

"""Общее представление информации о языке"""
class AdminAuthorDetailView(generic.DetailView):
    model = Author
    template_name = 'author/admin_author_detail.html'  # Новый шаблон для админки
    
    def get_object(self):
        author = super().get_object()
        return author

class AuthorDetailView(generic.DetailView):
    model = Author
    template_name = 'author/author_detail.html'
    
    def get_object(self):
        author = super().get_object()
        return author

"""Общее представление информации о жанре"""
class AdminGenreDetailView(generic.DetailView):
    model = Genre
    template_name = 'genre/admin_genre_detail.html'
    #context_object_name = 'admin-genre-detail'
    def get_object(self):
        genre = super().get_object()
        return genre

class GenreDetailView(generic.DetailView):
    model = Genre
    template_name = 'genre/genre_detail.html'
    def get_object(self):
        genre = super().get_object()
        return genre

"""Общее представление списка жанров на основе классов"""
class AdminGenreListView(generic.ListView):
    model = Genre
    paginate_by = 10
    template_name = 'genre/admin_genre_list.html'
    context_object_name = 'genre_list'
    
    def get_queryset(self):
        sort = self.request.GET.get('sort', 'name')
        return Genre.objects.all().order_by(sort)

class GenreListView(generic.ListView):
    model = Genre
    paginate_by = 10
    template_name = 'genre/genre_list.html'
    context_object_name = 'genre_list'
    
    def get_queryset(self):
        sort = self.request.GET.get('sort', 'name')
        return Genre.objects.all().order_by(sort)

"""Общее представление информации о языке"""
class AdminLanguageDetailView(generic.DetailView):
    model = Language
    template_name = 'language/admin_language_detail.html'
 
    def get_object(self):
        language = super().get_object()
        return language


class LanguageDetailView(generic.DetailView):
    model = Language
    template_name = 'language/language_detail.html'
    
    def get_object(self):
        language = super().get_object()
        return language

"""Общее представление списка языков"""
class AdminLanguageListView(generic.ListView):
    model = Language
    paginate_by = 10
    template_name = 'language/admin_language_list.html'
    context_object_name = 'language_list'

    def get_queryset(self):
        sort = self.request.GET.get('sort', 'name')  # Получаем параметр сортировки
        return Language.objects.all().order_by(sort)


class LanguageListView(generic.ListView):
    model = Language
    paginate_by = 10
    template_name = 'language/language_list.html'
    context_object_name = 'language_list'

    def get_queryset(self):
        sort = self.request.GET.get('sort', 'name')
        return Language.objects.all().order_by(sort)


class BookInstanceListView(generic.ListView):
    """Generic class-based view for a list of books."""
    model = BookInstance
    paginate_by = 10


class BookInstanceDetailView(generic.DetailView):
    """Generic class-based detail view for a book."""
    model = BookInstance


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


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


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


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/11/2023'}
    #template_name = 'author/author_form.html'
    permission_required = 'catalog.add_author'
    
        # Функция для проверки, является ли пользователь суперпользователем
    def test_func(self):
        return self.request.user.is_superuser

    # Если проверка не пройдена, перенаправляем пользователя
    def handle_no_permission(self):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Access denied: Only superusers can access this page.")


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    # Not recommended (potential security issue if more fields added)
    fields = '__all__'
    permission_required = 'catalog.change_author'
    
    def get_object(self):
        author = super().get_object()
        return author


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    template_name = 'author/author_confirm_delete.html'
    permission_required = 'catalog.delete_author'

    def get_object(self):
        author = super().get_object()
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
    template_name = 'book/book_form.html'
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language', 'path_to_icon', 'path_to_file']
    permission_required = 'catalog.add_book'


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    template_name = 'book/book_form.html'
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language', 'path_to_icon', 'path_to_file']
    permission_required = 'catalog.change_book'
    
    def get_object(self):
        book = super().get_object()
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
    template_name = 'book/book_confirm_delete.html'
    permission_required = 'catalog.delete_book'

    def get_object(self):
        book = super().get_object()
        return book


class GenreCreate(PermissionRequiredMixin, CreateView):
    model = Genre
    fields = ['name', ]
    permission_required = 'catalog.add_genre'


class GenreUpdate(PermissionRequiredMixin, UpdateView):
    model = Genre
    fields = ['name', ]
    permission_required = 'catalog.change_genre'

    def get_object(self):
        genre = super().get_object()
        return genre


class GenreDelete(PermissionRequiredMixin, DeleteView):
    model = Genre
    success_url = reverse_lazy('genres')
    permission_required = 'catalog.delete_genre'

    def get_object(self):
        genre = super().get_object()
        return genre


class LanguageCreate(PermissionRequiredMixin, CreateView):
    model = Language
    fields = ['name', ]
    permission_required = 'catalog.add_language'


class LanguageUpdate(PermissionRequiredMixin, UpdateView):
    model = Language
    fields = ['name', ]
    permission_required = 'catalog.change_language'

    def get_object(self):
        language = super().get_object()
        return language


class LanguageDelete(PermissionRequiredMixin, DeleteView):
    model = Language
    success_url = reverse_lazy('languages')
    permission_required = 'catalog.delete_language'

    def get_object(self):
        language = super().get_object()
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
