from datetime import datetime
from django.urls import resolve
from .models import Book, Author, Language, logs
import os
import json
from django.conf import settings

import xml.etree.ElementTree as ET
from django.http import HttpResponse
import xml.dom.minidom
class LogUserActionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Логировать только если пользователь аутентифицирован
        if request.user.is_authenticated:
            # Получаем информацию о маршруте (URL) запроса
            match = resolve(request.path)

            # Логирование для страницы книг с пагинацией
            if match.url_name == 'books':  # Страница списка книг с пагинацией
                # Получаем номер страницы из параметров запроса
                page = request.GET.get('page', 1)
                action_description = f"Visited book list, page {page}"
                
            elif match.url_name == 'authors': # Страница списка авторов с пагинацией
                page = request.GET.get('page', 1)
                action_description = f"Visited author list, page {page}"

            elif match.url_name == 'languages': 
                page = request.GET.get('page', 1)
                action_description = f"Visited language list, page {page}"
            
            elif match.url_name == 'log': 
                page = request.GET.get('page', 1)
                action_description = f"Visited log list, page {page}"
            
            # Логирование для страницы книги
            elif match.url_name == 'book-detail':  # Страница книги
                book_id = match.kwargs.get('pk')
                try:
                    book = Book.objects.get(pk=book_id)
                    action_description = f"Visited book: {book.title}"
                except Book.DoesNotExist:
                    action_description = f"Visited unknown book with id: {book_id}"

            # Логирование для страницы автора
            elif match.url_name == 'author-detail':  # Страница автора
                author_id = match.kwargs.get('pk')
                try:
                    author = Author.objects.get(pk=author_id)
                    action_description = f"Visited author: {author.first_name} {author.last_name}"
                except Author.DoesNotExist:
                    action_description = f"Visited unknown author with id: {author_id}"

            # Логирование для страницы языка
            elif match.url_name == 'language-detail':  # Страница языка
                language_id = match.kwargs.get('pk')
                try:
                    language = Language.objects.get(pk=language_id)
                    action_description = f"Visited language: {language.name}"
                except Language.DoesNotExist:
                    action_description = f"Visited unknown language with id: {language_id}"

            # Логирование других страниц
            else:
                # Используем request.get_full_path() для логирования полного URL с параметрами
                action_description = f"Visited {request.get_full_path()}"

            # Логируем действие
            log_entry = logs.objects.create(
                user=request.user,
                action=action_description,
                timestamp=datetime.now()
            )
            log_file_path = os.path.join(settings.BASE_DIR, 'logs.txt')
            with open(log_file_path, 'a') as file:
                file.write(f'{log_entry.timestamp} - {log_entry.user} - {log_entry.action}\n')
            
            json_file_path = os.path.join(settings.BASE_DIR, 'logs.json')
    
            log_data = {
                'timestamp': str(log_entry.timestamp),
                'user': str(log_entry.user),
                'action': log_entry.action,
            }

            logs_list = []
            
            # Проверяем, существует ли файл и не пустой ли он
            if os.path.exists(json_file_path) and os.path.getsize(json_file_path) > 0:
                with open(json_file_path, 'r') as file:
                    try:
                        logs_list = json.load(file)
                    except json.JSONDecodeError:
                        logs_list = []  # Если файл некорректен, создаем пустой список

            logs_list.append(log_data)

            with open(json_file_path, 'w') as file:
                json.dump(logs_list, file, indent=4)
                
            xml_file_path = 'logs.xml'

            # Создаем XML структуру для новой записи лога
            log_data = ET.Element('log')

            user = ET.SubElement(log_data, 'user')
            user.text = log_entry.user.username

            action = ET.SubElement(log_data, 'action')
            action.text = log_entry.action

            timestamp = ET.SubElement(log_data, 'timestamp')
            timestamp.text = log_entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")

            # Проверяем, существует ли файл
            if os.path.exists(xml_file_path):
                # Загружаем существующий XML файл без форматирования
                tree = ET.parse(xml_file_path)
                root = tree.getroot()
                root.append(log_data)
            else:
                # Если файл не существует, создаем корневой элемент
                root = ET.Element('logs')
                root.append(log_data)
                tree = ET.ElementTree(root)

            # Записываем в файл без отступов и лишних новых строк
            with open(xml_file_path, 'wb') as file:
                tree.write(file, encoding='utf-8', xml_declaration=True)

        return response
    
