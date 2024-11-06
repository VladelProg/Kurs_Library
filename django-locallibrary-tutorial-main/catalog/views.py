from django.views.decorators.http import require_POST

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Avg, Q
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
    paginate_by = 2
    template_name = 'book/book_list.html'
    context_object_name = 'book_list'

    def get_queryset(self):
        queryset = Book.objects.all().annotate(average_rating=Avg('ratings__rating'))
        
        # Проверка на наличие параметра сортировки в запросе
        sort = self.request.GET.get('sort')
        if sort:
            queryset = queryset.order_by(sort)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Передача параметра сортировки в шаблон для корректного отображения выбранной опции
        context['sort'] = self.request.GET.get('sort', 'title')
        return context


def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['sort'] = self.request.GET.get('sort', 'title')  # Передаем параметр сортировки
    return context

class BookDetailView(generic.DetailView):
    model = Book
    template_name = 'book/book_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Средний рейтинг книги
        context['average_rating'] = Rating.objects.filter(book_id=self.object.id).aggregate(Avg('rating'))['rating__avg']

        # Рейтинг текущего пользователя для данной книги, если он есть
        user_rating = Rating.objects.filter(book_id=self.object.id, user=str(self.request.user)).first()
        context['user_rating'] = user_rating.rating if user_rating else None
        
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



from django.core.paginator import Paginator

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


class AuthorDetailView(generic.DetailView):
    model = Author
    template_name = 'author/author_detail.html'
    
    def get_object(self):
        author = super().get_object()
        return author

class GenreDetailView(generic.DetailView):
    model = Genre
    template_name = 'genre/genre_detail.html'
    def get_object(self):
        genre = super().get_object()
        return genre

class GenreListView(generic.ListView):
    model = Genre
    paginate_by = 10
    template_name = 'genre/genre_list.html'
    context_object_name = 'genre_list'
    
    def get_queryset(self):
        sort = self.request.GET.get('sort', 'name')
        return Genre.objects.all().order_by(sort)


class LanguageDetailView(generic.DetailView):
    model = Language
    template_name = 'language/language_detail.html'
    
    def get_object(self):
        language = super().get_object()
        return language


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


# Classes created for the forms challenge

def book_list_view(request):
    sort = request.GET.get('sort', 'title')  # Параметр сортировки, по умолчанию сортировка по названию
    if sort not in ['title', '-title', 'rating', '-rating']:
        sort = 'title'  # Если передан неверный параметр, сортируем по названию
    
    books = Book.objects.all().order_by(sort)  # Сортируем по выбранному параметру
    return render(request, 'book_list.html', {'book_list': books, 'sort': sort})


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
