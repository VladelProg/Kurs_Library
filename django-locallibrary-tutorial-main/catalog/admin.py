from django.contrib import admin
from django.shortcuts import render
from django.urls import path
# Register your models here.
from django.views.generic import ListView
from django.views import generic, View
from django.shortcuts import render, get_object_or_404, redirect
from .models import Author, Genre, Book, BookInstance, Language, logs
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView

"""Minimal registration of Models.
admin.site.register(Book)
admin.site.register(Author)
admin.site.register(BookInstance)
admin.site.register(Genre)
admin.site.register(Language)
"""

admin.site.register(Genre)
admin.site.register(Language)


# Модели Book
class AdminBookListView(generic.ListView):
    model = Book
    paginate_by = 6
    template_name = 'book/admin_book_list.html'
    context_object_name = 'book-list'

    def get_queryset(self):
        sort = self.request.GET.get('sort', 'title')  # Получаем параметр сортировки
        return Book.objects.all().order_by(sort)

class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    template_name = 'book/book_form.html'
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language', 'path_to_icon', 'path_to_file']
    permission_required = 'catalog.change_book'
    
    def get_object(self):
        book = super().get_object()
        return book

class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    template_name = 'book/book_form.html'
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language', 'path_to_icon', 'path_to_file']
    permission_required = 'catalog.add_book'

class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('admin_books')
    template_name = 'book/book_confirm_delete.html'
    permission_required = 'catalog.delete_book'

    def get_object(self):
        book = super().get_object()
        return book

class BooksInline(admin.TabularInline):
    """Defines format of inline book insertion (used in AuthorAdmin)"""
    model = Book

class AdminBookDetailView(generic.DetailView):
    model = Book
    template_name = 'book/admin_book_detail.html'
    def get_object(self):
        book = super().get_object()
        return book
    
    
"""Модель Language
    Общее представление информации о языке"""
    
class AdminLanguageDetailView(generic.DetailView):
    model = Language
    template_name = 'language/admin_language_detail.html'
 
    def get_object(self):
        language = super().get_object()
        return language

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
    success_url = reverse_lazy('admin_languages')
    permission_required = 'catalog.delete_language'

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


# Модели Author

"""Общее представление информации о авторе"""
class AdminAuthorDetailView(generic.DetailView):
    model = Author
    template_name = 'author/admin_author_detail.html'
    
    def get_object(self):
        author = super().get_object()
        return author

class AdminAuthorListView(generic.ListView):
    model = Author
    paginate_by = 2
    template_name = 'author/admin_author_list.html'
    context_object_name = 'admin_author_list'
    
    def get_queryset(self):
        sort = self.request.GET.get('sort', 'last_name')
        return Author.objects.all().order_by(sort)


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/11/2023'}
    template_name = 'catalog/author_form.html'
    permission_required = 'catalog.add_author'

    def get_success_url(self):
        return reverse_lazy('admin-author-detail', kwargs={'pk': self.object.pk})


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = '__all__'
    permission_required = 'catalog.change_author'
    
    def get_success_url(self):
        return reverse_lazy('admin-update', kwargs={'pk': self.object.pk})


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('admin_authors')  # Убедитесь, что 'admin-author-list' - это правильное имя URL
    template_name = 'author/author_confirm_delete.html'
    permission_required = 'catalog.delete_author'


""" Модели Genre
    Общее представление списка жанров"""
class AdminGenreListView(generic.ListView):
    model = Genre
    paginate_by = 10
    template_name = 'genre/admin_genre_list.html'
    context_object_name = 'genre_list'
    
    def get_queryset(self):
        sort = self.request.GET.get('sort', 'name')
        return Genre.objects.all().order_by(sort)

"""Общее представление информации о жанре"""
class AdminGenreDetailView(generic.DetailView):
    model = Genre
    template_name = 'genre/admin_genre_detail.html'
    #context_object_name = 'admin-genre-detail'
    def get_object(self):
        genre = super().get_object()
        return genre

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
    success_url = reverse_lazy('admin_genres')
    permission_required = 'catalog.delete_genre'

    def get_object(self):
        genre = super().get_object()
        return genre

# Вход admin

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

# Модель logs

class AdminShowData(UserPassesTestMixin, ListView):
    model = logs
    paginate_by = 20
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


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Administration object for Author models.
    Defines:
     - fields to be displayed in list view (list_display)
     - orders fields in detail view (fields),
       grouping the date fields horizontally
     - adds inline addition of books in author view (inlines)
    """
    list_display = ('last_name',
                    'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BooksInline]


class BooksInstanceInline(admin.TabularInline):
    """Defines format of inline book instance insertion (used in BookAdmin)"""
    model = BookInstance


class BookAdmin(admin.ModelAdmin):
    """Administration object for Book models.
    Defines:
     - fields to be displayed in list view (list_display)
     - adds inline addition of book instances in book view (inlines)
    """
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]


admin.site.register(Book, BookAdmin)


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    """Administration object for BookInstance models.
    Defines:
     - fields to be displayed in list view (list_display)
     - filters that will be displayed in sidebar (list_filter)
     - grouping of fields into sections (fieldsets)
    """
    list_display = ('book', 'status', 'borrower', 'due_back', 'id')
    list_filter = ('status', 'due_back')

    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )

#@admin.register(AdminPanel)
#class UserActionLogAdmin(admin.ModelAdmin):
#    list_display = ('action', 'timestamp')
#    list_filter = ('timestamp')
#    search_fields = ('action')