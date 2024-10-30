from django.urls import include, path
from .views import AdminLoginView
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('admin_zone/login/', AdminLoginView.as_view(), name='admin_login'),
    path('admin_panel/', views.AdminPanelView.as_view(), name='admin_panel'),
    path('admin_panel/logs/', views.AdminShowData.as_view(), name='log'),
    
    path('books/', views.BookListView.as_view(), name='books'),
    path('admin_panel/books/', views.AdminBookListView.as_view(), name='admin_books'),
    path('admin_panel/book/<int:pk>', views.AdminBookDetailView.as_view(), name='admin-book-detail'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('admin_panel/authors/', views.AdminAuthorListView.as_view(), name='admin_authors'),
    path('author/<int:pk>',
         views.AuthorDetailView.as_view(), name='author-detail'),
    path('admin_panel/author/<int:pk>',
         views.AdminAuthorDetailView.as_view(), name='admin-author-detail'),
    
]


urlpatterns += [
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    path(r'borrowed/', views.LoanedBooksAllListView.as_view(), name='all-borrowed'),  # Added for challenge
]


# Ссылки на возврат книги
urlpatterns += [
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
]


# Ссылки на добавление, обновление, удаление информации об авторах книг
urlpatterns += [
    path('admin_zone/author/create/', views.AuthorCreate.as_view(), name='author-create'),
    path('admin_zone/author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author-update'),
    path('admin_zone/author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author-delete'),
]

# Add URLConf to create, update, and delete books
urlpatterns += [
    path('book/create/', views.BookCreate.as_view(), name='book-create'),
    path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book-update'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book-delete'),
    path('books/<int:book_id>/add_rating/', views.add_rating, name='add_rating'),
    
]


# Add URLConf to list, view, create, update, and delete genre
urlpatterns += [
    path('admin_panel/genres/', views.AdminGenreListView.as_view(), name='admin_genres'),
    path('genres/', views.GenreListView.as_view(), name='genres'),
    
    path('genre/<int:pk>', views.GenreDetailView.as_view(), name='genre-detail'),
    path('admin_zone/genre/create/', views.GenreCreate.as_view(), name='genre-create'),
    path('admin_zone/genre/<int:pk>/update/', views.GenreUpdate.as_view(), name='genre-update'),
    path('admin_zone/genre/<int:pk>/delete/', views.GenreDelete.as_view(), name='genre-delete'),
]

# Add URLConf to list, view, create, update, and delete languages
urlpatterns += [
    path('languages/', views.LanguageListView.as_view(), name='languages'),
    
    path('admin_panel/languages/', views.AdminLanguageListView.as_view(), name='admin_languages'),
    path('admin_zone/language/<int:pk>', views.AdminLanguageDetailView.as_view(),
         name='admin-language-detail'),
    path('language/<int:pk>', views.LanguageDetailView.as_view(),
         name='language-detail'),
    
    path('admin_zone/language/create/', views.LanguageCreate.as_view(), name='language-create'),
    path('admin_zone/language/<int:pk>/update/',
         views.LanguageUpdate.as_view(), name='language-update'),
    path('admin_zone/language/<int:pk>/delete/',
         views.LanguageDelete.as_view(), name='language-delete'),
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
