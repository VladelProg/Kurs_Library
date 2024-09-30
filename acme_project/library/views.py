from django.core.paginator import Paginator
from django.shortcuts import render
from .models import LibraryFile

def library_view(request):
    files = LibraryFile.objects.all()
    paginator = Paginator(files, 10)  # Пагинация: по 10 файлов на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'library/library_view.html', {'page_obj': page_obj})
