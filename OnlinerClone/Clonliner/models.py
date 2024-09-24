from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save


# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, help_text="Введите юзернейм пользователя",
                                verbose_name="Юзернейм пользователя")
    full_name = models.CharField(max_length=200, help_text="Введите полное имя пользователя",
                                 verbose_name="Полное имя пользователя")
    address = models.CharField(max_length=200, null=True, blank=True, help_text="Введите адрес пользователя",
                               verbose_name="Адрес пользователя")
    joined_on = models.DateTimeField(default=timezone.now, help_text="Введите дату регистрации пользователя",
                                     verbose_name="Дата регистрации пользователя")

    objects = models.Model

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Клиент"  # Название в единственном числе
        verbose_name_plural = "Клиенты"  # Название в единственном числе
        ordering = ["full_name"]  # Сортировка по полю (если с "-" то в обратном порядке)


class Categories(models.Model):
    name = models.CharField(max_length=200, help_text="Введите название категории", verbose_name="Имя категории",
                            null=True, blank=True)
    objects = models.Model

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок", help_text="Введите заголовок объявления")
    photo = models.ImageField(null=True, blank=True, upload_to="post_photos", verbose_name="Фото", help_text="Фотографии объявления")
    description = models.TextField(verbose_name="Описание", help_text="Введите описание объявления")
    price = models.DecimalField(verbose_name="Цена", max_digits=10, decimal_places=2,
                                help_text="Введите цену объявления")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Кем создано",
                                   help_text="Автор объявления")
    created_on = models.DateTimeField(default=timezone.now, verbose_name="Когда создано",
                                      help_text="Дата создания объявления")
    views = models.PositiveIntegerField(default=0, verbose_name="Количество просмотров",
                                        help_text="Количество просмотров объявления")
    category = models.ForeignKey(Categories, null=True, blank=True, verbose_name="Категория", on_delete=models.PROTECT,
                                 help_text="Категория объявления")
    objects = models.Model

    def __str__(self):
        return str(self.title) + " " + str(self.created_by)

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ["-created_on"]  # Сортировка по убыванию даты создания


class Chat(models.Model):
    users = models.ManyToManyField(User, related_name='chats')

    objects = models.Model

    def __str__(self):
        usernames = [user.username for user in self.users.all()]
        return f"Чат между {', '.join(usernames)}"


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, verbose_name="Чат", help_text="Выберите чат",
                             related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Отправитель",
                               help_text="Введите отправителя")
    content = models.TextField(verbose_name="Текст сообщения", help_text="Введите текст сообщения")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Время отправления",
                                     help_text="Введите время отправления")
    status = models.CharField(max_length=10, choices=[('seen', 'Seen'), ('unseen', 'Unseen')], default='unseen',
                              verbose_name="Статус сообщения", help_text="Статус сообщения")
    objects = models.Model

    def __str__(self):
        return f"Сообщение от {self.sender.username} в чате {self.chat}"
