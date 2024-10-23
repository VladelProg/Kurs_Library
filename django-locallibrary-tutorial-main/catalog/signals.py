from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Book, logs, Language, Genre, Author
from django.contrib.auth.models import User
from datetime import datetime

# Для книги
@receiver(post_save, sender=Book)
def log_book_addition(sender, instance, created, **kwargs):
    if created:  # Это значит, что объект был создан, а не обновлен
        logs.objects.create(
            user=User.objects.get(username='admin'),  # Укажите пользователя, который добавляет запись
            action=f"Book '{instance.title}' by {instance.author} was added.",
             timestamp=datetime.now()
        )
    if not created:  # Проверяем, что объект обновлен, а не создан
        logs.objects.create(
            user=User.objects.get(username='admin'),  # Укажите пользователя, который добавляет запись
            action=f"Book '{instance.title}' by {instance.author} was updated.",
             timestamp=datetime.now()
        )

@receiver(post_delete, sender=Book)
def log_book_deletion(sender, instance, **kwargs):
    logs.objects.create(
        user=User.objects.get(username='admin'),  # Укажите пользователя, который удаляет запись
        action=f"Book '{instance.title}' was deleted.",
    )

# Для языка

@receiver(post_save, sender=Language)
def log_lang_addition(sender, instance, created, **kwargs):
    if created:  # Это значит, что объект был создан, а не обновлен
        logs.objects.create(
            user=User.objects.get(username='admin'),  # Укажите пользователя, который добавляет запись
            action=f"Language '{instance.name}'  was added into base.",
            timestamp=datetime.now()
        )
    if not created:  # Проверяем, что объект обновлен, а не создан
        logs.objects.create(
            user=User.objects.get(username='admin'),  # Укажите пользователя, который обновляет запись
            action=f"Language '{instance.name}' was updated.",
        )

@receiver(post_delete, sender=Language)
def log_lang_deletion(sender, instance, **kwargs):
    logs.objects.create(
        user=User.objects.get(username='admin'),  # Укажите пользователя, который удаляет запись
        action=f"Language '{instance.name}' was deleted.",
    )

# Для жанра

@receiver(post_save, sender=Genre)
def log_genre_addition(sender, instance, created, **kwargs):
    if created:  # Это значит, что объект был создан, а не обновлен
        logs.objects.create(
            user=User.objects.get(username='admin'),  # Укажите пользователя, который добавляет запись
            action=f"Genre '{instance.name}' was added into base.",
            timestamp=datetime.now()
        )
    if not created:  # Проверяем, что объект обновлен, а не создан
        logs.objects.create(
            user=User.objects.get(username='admin'),  # Укажите пользователя, который обновляет запись
            action=f"Genre '{instance.name}' was updated.",
        )

@receiver(post_delete, sender=Genre)
def log_genre_deletion(sender, instance, **kwargs):
    logs.objects.create(
        user=User.objects.get(username='admin'),  # Укажите пользователя, который удаляет запись
        action=f"Genre {instance.name} was deleted.",
    )

# Для автора

@receiver(post_save, sender=Author)
def log_author_addition(sender, instance, created, **kwargs):
    if created:  # Это значит, что объект был создан, а не обновлен
        logs.objects.create(
            user=User.objects.get(username='admin'),  # Укажите пользователя, который добавляет запись
            action=f"Author {instance.first_name} {instance.last_name} was added into base.",
            timestamp=datetime.now()
        )
    if not created:  # Проверяем, что объект обновлен, а не создан
        logs.objects.create(
            user=User.objects.get(username='admin'),  # Укажите пользователя, который обновляет запись
            action=f"Author {instance.first_name} {instance.last_name} was updated.",
        )

@receiver(post_delete, sender=Author)
def log_author_deletion(sender, instance, **kwargs):
    logs.objects.create(
        user=User.objects.get(username='admin'),  # Укажите пользователя, который удаляет запись
        action=f"Author {instance.first_name} {instance.last_name} was deleted.",
    )