from django.urls import include, path
from . import views
from . import admin

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),
]


urlpatterns += [
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    path(r'borrowed/', views.LoanedBooksAllListView.as_view(), name='all-borrowed'),  # Added for challenge
]


# Ссылки на возврат книги
urlpatterns += [
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
]


# Add URLConf to create, update, and delete books
urlpatterns += [

    path('books/<int:book_id>/add_rating/', views.add_rating, name='add_rating'),
]

# Все admin зоны
urlpatterns += [
     
     # Вход
     path('admin_zone/login/', admin.AdminLoginView.as_view(), name='admin_login'),
     path('admin_panel/', admin.AdminPanelView.as_view(), name='admin_panel'),
     
     # Логи серевера (class logs)
     path('admin_panel/logs/', admin.AdminShowData.as_view(), name='log'),
     
     # Книги (class Book)
     path('admin_panel/books/', admin.AdminBookListView.as_view(), name='admin_books'),
     path('admin_panel/book/<int:pk>', admin.AdminBookDetailView.as_view(), name='admin-book-detail'),
     path('admin_zone/book/create/', admin.BookCreate.as_view(), name='book-create'), # создание книги
     path('admin_zone/book/<int:pk>/update/', admin.BookUpdate.as_view(), name='book-update'), # обновление данных
     path('admin_zone/book/<int:pk>/delete/', admin.BookDelete.as_view(), name='book-delete'), # удаление книги
     
     # Авторы (class Author)
     path('admin_panel/authors/', admin.AdminAuthorListView.as_view(), name='admin_authors'),
     path('admin_panel/author/<int:pk>', admin.AdminAuthorDetailView.as_view(), name='admin-author-detail'),
     path('admin_zone/author/create/', admin.AuthorCreate.as_view(), name='author-create'),
     path('admin_zone/author/<int:pk>/update/', admin.AuthorUpdate.as_view(), name='author-update'),
     path('admin_zone/author/<int:pk>/delete/', admin.AuthorDelete.as_view(), name='author-delete'),
     
     # Жанры
     path('admin_panel/genres/', admin.AdminGenreListView.as_view(), name='admin_genres'),
     path('admin_zone/genre/<int:pk>', admin.AdminGenreDetailView.as_view(), name='admin-genre-detail'),
     path('admin_zone/genre/create/', admin.GenreCreate.as_view(), name='genre-create'),
     path('admin_zone/genre/<int:pk>/update/', admin.GenreUpdate.as_view(), name='genre-update'),
     path('admin_zone/genre/<int:pk>/delete/', admin.GenreDelete.as_view(), name='genre-delete'),
    
     # Языки (class Language)
     path('admin_panel/languages/', admin.AdminLanguageListView.as_view(), name='admin_languages'),
     path('admin_zone/language/<int:pk>', admin.AdminLanguageDetailView.as_view(), name='admin-language-detail'),
     path('admin_zone/language/create/', admin.LanguageCreate.as_view(), name='language-create'),
     path('admin_zone/language/<int:pk>/update/', admin.LanguageUpdate.as_view(), name='language-update'),
     path('admin_zone/language/<int:pk>/delete/', admin.LanguageDelete.as_view(), name='language-delete'),    
]

# Add URLConf to list, view, create, update, and delete genre
urlpatterns += [
    path('genres/', views.GenreListView.as_view(), name='genres'),
    path('genre/<int:pk>', views.GenreDetailView.as_view(), name='genre-detail'),
    
]

# Add URLConf to list, view, create, update, and delete languages
urlpatterns += [
    path('languages/', views.LanguageListView.as_view(), name='languages'),
    path('language/<int:pk>', views.LanguageDetailView.as_view(),
         name='language-detail'),
]

# Add URLConf to list, view, create, update, and delete bookinstances
urlpatterns += [
    path('bookinstances/', views.BookInstanceListView.as_view(), name='bookinstances'),
    path('bookinstance/<uuid:pk>', views.BookInstanceDetailView.as_view(),
         name='bookinstance-detail'),
    path('bookinstance/create/', views.BookInstanceCreate.as_view(),
         name='bookinstance-create'),
    path('bookinstance/<uuid:pk>/update/',
         views.BookInstanceUpdate.as_view(), name='bookinstance-update'),
    path('bookinstance/<uuid:pk>/delete/',
         views.BookInstanceDelete.as_view(), name='bookinstance-delete'),
]
