from datetime import date

from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_GUEST = 'guest'
    ROLE_CLIENT = 'client'
    ROLE_TOUR_AGENT = 'tour_agent'
    ROLE_MANAGER = 'manager'
    ROLE_ADMIN = 'admin'
    ROLE_OPERATOR = 'operator'

    ROLES_CHOICES = [
        (ROLE_GUEST, 'Гость'),
        (ROLE_CLIENT, 'Клиент'),
        (ROLE_TOUR_AGENT, 'Турагент'),
        (ROLE_MANAGER, 'Менеджер / Сотрудник поддержки'),
        (ROLE_ADMIN, 'Администратор сайта'),
        (ROLE_OPERATOR, 'Туроператор'),
    ]

    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон")
    role = models.CharField(max_length=50, choices=ROLES_CHOICES, default=ROLE_GUEST, verbose_name="Роль")
    date_registered = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название страны")

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"
        ordering = ['name']

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название города")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='cities', verbose_name="Страна")

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"
        unique_together = ('name', 'country')
        ordering = ['name']

    def __str__(self):
        return f"{self.name}, {self.country.name}"


class Hotel(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название отеля")
    stars = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name="Количество звёзд")
    address = models.CharField(max_length=255, verbose_name="Адрес")
    description = models.TextField(verbose_name="Описание")
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Страна")
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Город")
    images = models.ManyToManyField('Image', blank=True,
                                    verbose_name="Изображения отеля")  # <-- ЭТУ СТРОКУ НУЖНО ДОБАВИТЬ ОБРАТНО

    class Meta:
        verbose_name = "Отель"
        verbose_name_plural = "Отели"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.stars}*)"


class Image(models.Model):
    image = models.ImageField(upload_to='tour_images/', verbose_name="Файл изображения")
    caption = models.CharField(max_length=255, blank=True, verbose_name="Подпись")

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"

    def __str__(self):
        return self.caption or self.image.name


class Tour(models.Model):
    TOUR_TYPES = [
        ('beach', 'Пляжный отдых'),
        ('excursion', 'Экскурсионный'),
        ('adventure', 'Приключения'),
        ('ski', 'Горнолыжный'),
        ('cruise', 'Круиз'),
        ('medical', 'Оздоровительный'),
        ('business', 'Деловой'),
        ('other', 'Другое'),
    ]

    title = models.CharField(max_length=200, verbose_name="Название тура")
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, verbose_name="Страна")
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, verbose_name="Город")
    hotel = models.ForeignKey(Hotel, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Отель")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    duration = models.IntegerField(verbose_name="Продолжительность (дни)")
    available_slots = models.IntegerField(verbose_name="Доступные места")
    tour_type = models.CharField(max_length=50, choices=TOUR_TYPES, default='other', verbose_name="Тип тура")
    description = models.TextField(verbose_name="Описание тура")
    main_image = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='tours_main_image', verbose_name="Главное изображение")
    images = models.ManyToManyField(Image, blank=True, related_name='tours_gallery', verbose_name="Галерея изображений")

    class Meta:
        verbose_name = "Тур"
        verbose_name_plural = "Туры"
        ordering = ['start_date']

    def __str__(self):
        return self.title

    def is_active(self):
        return self.available_slots > 0 and self.end_date >= date.today()


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', verbose_name="Пользователь")
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='bookings', verbose_name="Тур")
    num_people = models.IntegerField(verbose_name="Количество человек")
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
        ('completed', 'Завершено'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    booking_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата бронирования")

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ['-booking_date']

    def __str__(self):
        return f"Бронирование {self.id} на тур '{self.tour.title}' от {self.user.username}"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name="Пользователь")
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True,
                             verbose_name="Тур")
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True,
                              verbose_name="Отель")
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name="Оценка")
    text = models.TextField(verbose_name="Текст отзыва")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Отзыв на {self.tour.title if self.tour else self.hotel.name if self.hotel else 'неизвестно'}"


class Promotion(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название акции")
    description = models.TextField(verbose_name="Описание акции")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    tours = models.ManyToManyField(Tour, blank=True, related_name='promotions', verbose_name="Туры по акции")
    countries = models.ManyToManyField(Country, blank=True, related_name='promotions', verbose_name="Страны по акции")

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        today = date.today()
        return self.start_date <= today <= self.end_date

    @admin.display(description='Активна')
    def get_is_active_display(self):
        return "Да" if self.is_active else "Нет"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name="Пользователь")
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='favorites', verbose_name="Тур")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные туры"
        unique_together = ('user', 'tour')
        ordering = ['-added_at']

    def __str__(self):
        return f"Тур '{self.tour.title}' в избранном у {self.user.username}"
