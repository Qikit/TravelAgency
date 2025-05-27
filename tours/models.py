from datetime import date

from django.db import models
from django.contrib.auth.models import AbstractUser  # Для расширения стандартной модели пользователя
from django.contrib import admin


class User(AbstractUser):
    # Роли пользователя
    ROLE_GUEST = 'guest'
    ROLE_CLIENT = 'client'
    ROLE_TOUR_AGENT = 'tour_agent'
    ROLE_MANAGER = 'manager'
    ROLE_ADMIN = 'admin'
    ROLE_OPERATOR = 'operator'  # Добавим роль оператора из таблицы с ролями

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
        return f"{self.first_name} {self.last_name} ({self.role})" if self.first_name and self.last_name else self.username


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
        unique_together = ('name', 'country')  # Город уникален в рамках страны
        ordering = ['name']

    def __str__(self):
        return f"{self.name}, {self.country.name}"


class Hotel(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название отеля")
    stars = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)],
                                             verbose_name="Количество звёзд")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Адрес")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    images = models.ManyToManyField('Image', blank=True, verbose_name="Изображения")  # Ссылка на отдельную модель Image
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True,
                                verbose_name="Страна")  # Добавлено для удобства поиска и фильтрации
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True,
                             verbose_name="Город")  # Добавлено для удобства поиска и фильтрации

    class Meta:
        verbose_name = "Отель"
        verbose_name_plural = "Отели"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.stars}*) - {self.city.name if self.city else 'Неизвестно'}"


class Tour(models.Model):
    TOUR_TYPES = [
        ('beach', 'Пляжный'),
        ('excursion', 'Экскурсионный'),
        ('ski', 'Горнолыжный'),
        ('cruise', 'Круиз'),
        ('adventure', 'Приключенческий'),
        ('health', 'Оздоровительный'),
    ]

    title = models.CharField(max_length=255, verbose_name="Название")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='tours', verbose_name="Страна")
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='tours', verbose_name="Город")
    hotel = models.ForeignKey(Hotel, on_delete=models.SET_NULL, null=True, blank=True, related_name='tours',
                              verbose_name="Отель")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    duration = models.PositiveSmallIntegerField(verbose_name="Продолжительность (ночей)")  # Длительность
    available_slots = models.PositiveIntegerField(default=1,
                                                  verbose_name="Количество доступных мест")  # Количество доступных мест
    tour_type = models.CharField(max_length=50, choices=TOUR_TYPES, verbose_name="Тип тура")
    description = models.TextField(blank=True, null=True, verbose_name="Описание тура")  # Добавим описание
    main_image = models.ForeignKey('Image', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='main_for_tours',
                                   verbose_name="Главное изображение")  # Главное изображение тура
    images = models.ManyToManyField('Image', blank=True, related_name='tours',
                                    verbose_name="Дополнительные изображения")  # Дополнительные изображения тура

    class Meta:
        verbose_name = "Тур"
        verbose_name_plural = "Туры"
        ordering = ['start_date', 'price']

    def __str__(self):
        return f"{self.title} ({self.country.name}, {self.city.name})"

    @property
    def is_active(self):
        """Проверяет, активен ли тур (даты актуальны и есть места)."""
        return self.end_date >= models.DateField.today() and self.available_slots > 0

    @admin.display(description='Активен')
    def get_is_active_display(self):
        return "Да" if self.is_active else "Нет"


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', verbose_name="Пользователь")
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='bookings', verbose_name="Тур")
    booking_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата бронирования")  # Дата создания
    num_people = models.PositiveSmallIntegerField(default=1, verbose_name="Количество человек")  # Количество человек
    STATUS_CHOICES = [
        ('pending', 'Ожидание'),
        ('paid', 'Оплачено'),
        ('cancelled', 'Отменено'),
        ('confirmed', 'Подтверждено'),  # Добавим статус подтверждено
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ['-booking_date']

    def __str__(self):
        return f"Бронирование #{self.id} от {self.user.username} на тур '{self.tour.title}'"

    @admin.display(description='Общая стоимость')
    def total_cost(self):
        return self.tour.price * self.num_people


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name="Пользователь")
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews',
                             verbose_name="Тур")
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews',
                              verbose_name="Отель")
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)],
                                              verbose_name="Оценка (1-5)")  # Оценка
    text = models.TextField(verbose_name="Текст отзыва")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")  # Дата

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']

    def __str__(self):
        target = self.tour.title if self.tour else self.hotel.name if self.hotel else 'Неизвестно'
        return f"Отзыв от {self.user.username} на {target} (Оценка: {self.rating})"


class Promotion(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название акции")
    description = models.TextField(verbose_name="Описание")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    tours = models.ManyToManyField(Tour, blank=True, related_name='promotions', verbose_name="Привязанные туры")
    countries = models.ManyToManyField(Country, blank=True, related_name='promotions',
                                       verbose_name="Привязанные страны")

    class Meta:
        verbose_name = "Акция / Спецпредложение"
        verbose_name_plural = "Акции / Спецпредложения"
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        """Проверяет, активна ли акция."""
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
        unique_together = ('user', 'tour')  # Пользователь может добавить один тур в избранное только один раз
        ordering = ['-added_at']

    def __str__(self):
        return f"Тур '{self.tour.title}' в избранном у {self.user.username}"


class Image(models.Model):
    image = models.ImageField(upload_to='tour_images/', verbose_name="Изображение")
    caption = models.CharField(max_length=255, blank=True, verbose_name="Подпись")

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"

    def __str__(self):
        return self.caption if self.caption else f"Изображение {self.id}"