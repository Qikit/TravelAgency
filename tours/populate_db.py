# tour_agency/tours/populate_db.py

import os
import django
import random
from datetime import date, timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date

# Настройка Django окружения
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tour_agency.settings')
django.setup()

from tours.models import (
    User, Country, City, Hotel, Tour, Booking, Review, Promotion, Favorite, Image
)
from django.contrib.auth.hashers import make_password  # Для хеширования паролей


# --- Вспомогательные функции для создания данных ---

def create_random_image(caption="Placeholder"):
    """Создает имитацию изображения."""
    from io import BytesIO
    from PIL import Image as PILImage  # Используем PIL Image для создания заглушки
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    dummy_image = PILImage.new('RGB', (400, 300), color=color)
    buffer = BytesIO()
    dummy_image.save(buffer, format="PNG")
    file_name = f"{caption.replace(' ', '_').lower()}_{random.randint(1000, 9999)}.png"
    uploaded_file = SimpleUploadedFile(file_name, buffer.getvalue(), content_type="image/png")
    return Image.objects.create(image=uploaded_file, caption=caption)


def create_countries_cities():
    countries_data = {
        "Италия": ["Рим", "Венеция", "Флоренция", "Милан", "Неаполь"],
        "Франция": ["Париж", "Ницца", "Марсель", "Лион", "Бордо"],
        "Таиланд": ["Бангкок", "Пхукет", "Самуи", "Чиангмай", "Паттайя"],
        "Турция": ["Анталия", "Стамбул", "Кемер", "Аланья", "Бодрум"],
        "Египет": ["Шарм-эль-Шейх", "Хургада", "Каир", "Луксор", "Марса-Алам"],
        "Греция": ["Афины", "Салоники", "Родос", "Крит", "Корфу"],
        "Испания": ["Барселона", "Мадрид", "Валенсия", "Севилья", "Малага"],
        "ОАЭ": ["Дубай", "Абу-Даби"],
        "Мальдивы": ["Мале"],
        "Доминикана": ["Пунта-Кана"]
    }
    created_countries = []
    created_cities = []
    print("Создаем страны и города...")
    for country_name, cities_list in countries_data.items():
        country, created = Country.objects.get_or_create(name=country_name)
        if created:
            print(f"  Создана страна: {country.name}")
        created_countries.append(country)
        for city_name in cities_list:
            city, created = City.objects.get_or_create(name=city_name, country=country)
            if created:
                print(f"    Создан город: {city.name}, {country.name}")
            created_cities.append(city)
    return created_countries, created_cities


def create_users():
    users_data = [
        {"username": "admin", "email": "admin@example.com", "first_name": "Главный", "last_name": "Админ",
         "role": User.ROLE_ADMIN, "password": "adminpassword"},
        {"username": "agent1", "email": "agent1@example.com", "first_name": "Ирина", "last_name": "Агент",
         "role": User.ROLE_TOUR_AGENT, "password": "agentpassword"},
        {"username": "manager1", "email": "manager1@example.com", "first_name": "Олег", "last_name": "Менеджер",
         "role": User.ROLE_MANAGER, "password": "managerpassword"},
        {"username": "operator1", "email": "operator1@example.com", "first_name": "Анна", "last_name": "Оператор",
         "role": User.ROLE_OPERATOR, "password": "operatorpassword"},
        {"username": "client1", "email": "client1@example.com", "first_name": "Елена", "last_name": "Клиент",
         "role": User.ROLE_CLIENT, "password": "clientpassword"},
        {"username": "client2", "email": "client2@example.com", "first_name": "Сергей", "last_name": "Клиент",
         "role": User.ROLE_CLIENT, "password": "clientpassword"},
        {"username": "client3", "email": "client3@example.com", "first_name": "Дарья", "last_name": "Клиент",
         "role": User.ROLE_CLIENT, "password": "clientpassword"},
        {"username": "client4", "email": "client4@example.com", "first_name": "Максим", "last_name": "Клиент",
         "role": User.ROLE_CLIENT, "password": "clientpassword"},
        {"username": "client5", "email": "client5@example.com", "first_name": "Юлия", "last_name": "Клиент",
         "role": User.ROLE_CLIENT, "password": "clientpassword"},
        {"username": "client6", "email": "client6@example.com", "first_name": "Николай", "last_name": "Клиент",
         "role": User.ROLE_CLIENT, "password": "clientpassword"},
    ]
    created_users = []
    print("Создаем пользователей...")
    for data in users_data:
        password = data.pop("password")
        user, created = User.objects.get_or_create(username=data["username"], defaults={
            **data,
            'password': make_password(password),
            'is_staff': data['role'] in [User.ROLE_ADMIN, User.ROLE_MANAGER, User.ROLE_TOUR_AGENT, User.ROLE_OPERATOR],
            'is_superuser': data['role'] == User.ROLE_ADMIN
        })
        if created:
            print(f"  Создан пользователь: {user.username} ({user.role})")
        created_users.append(user)
    return created_users


def populate_database():
    print("Начинаем заполнение базы данных...")

    # Удаляем существующие данные (опционально, для чистоты)
    # print("Очищаем базу данных...")
    # Favorite.objects.all().delete()
    # Booking.objects.all().delete()
    # Review.objects.all().delete()
    # Tour.objects.all().delete()
    # Hotel.objects.all().delete()
    # Promotion.objects.all().delete()
    # City.objects.all().delete()
    # Country.objects.all().delete()
    # User.objects.exclude(is_superuser=True).delete() # Оставляем суперюзера
    # Image.objects.all().delete()
    # print("База данных очищена (кроме суперюзеров).")

    # 1. Страны и города
    countries, cities = create_countries_cities()
    if not countries or not cities:
        print("Не удалось создать страны/города. Прерываем заполнение.")
        return

    # 2. Пользователи
    users = create_users()
    if not users:
        print("Не удалось создать пользователей. Прерываем заполнение.")
        return
    clients = [u for u in users if u.role == User.ROLE_CLIENT]

    # 3. Изображения
    images = []
    print("Создаем изображения...")
    for i in range(20):  # Создадим 20 случайных изображений
        images.append(create_random_image(f"Изображение {i + 1}"))
    if not images:
        print("Не удалось создать изображения. Прерываем заполнение.")
        return

    # 4. Отели
    hotels = []
    print("Создаем отели...")
    for i in range(15):  # Минимум 10 отелей
        random_city = random.choice(cities)
        hotel_name = f"Отель {random_city.name} {i + 1}"
        hotel_stars = random.randint(3, 5)
        hotel_description = f"Роскошный отель с {hotel_stars} звёздами в прекрасном городе {random_city.name}."
        hotel = Hotel.objects.create(
            name=hotel_name,
            stars=hotel_stars,
            address=f"Ул. Примерная, {i + 1}",
            description=hotel_description,
            country=random_city.country,
            city=random_city
        )
        # Добавляем случайные изображения к отелю
        num_hotel_images = random.randint(1, 3)
        for _ in range(num_hotel_images):
            hotel.images.add(random.choice(images))
        hotels.append(hotel)
        print(f"  Создан отель: {hotel.name} ({hotel.stars}*)")
    if not hotels:
        print("Не удалось создать отели. Прерываем заполнение.")
        return

    # 5. Туры
    tours = []
    tour_types = [t[0] for t in Tour.TOUR_TYPES]
    print("Создаем туры...")
    today = date.today()
    for i in range(20):  # Минимум 10 туров, создадим 20 для разнообразия
        random_city = random.choice(cities)
        random_hotel = random.choice([h for h in hotels if
                                      h.city == random_city] or hotels)  # Стараемся выбрать отель из того же города, если есть

        start_date = today + timedelta(days=random.randint(-30, 90))  # От 30 дней назад до 90 дней вперед
        duration = random.randint(5, 14)
        end_date = start_date + timedelta(days=duration)
        price = random.randint(50000, 250000)
        available_slots = random.randint(0, 30)  # Некоторые могут быть заняты

        tour_title = f"Тур в {random_city.name} на {duration} ночей"
        tour_description = f"Потрясающий тур в {random_city.name}, включающий проживание в {random_hotel.name if random_hotel else 'прекрасном отеле'} и насыщенную программу. Отправляйтесь в незабываемое приключение!"

        tour = Tour.objects.create(
            title=tour_title,
            country=random_city.country,
            city=random_city,
            hotel=random_hotel,
            price=price,
            start_date=start_date,
            end_date=end_date,
            duration=duration,
            available_slots=available_slots,
            tour_type=random.choice(tour_types),
            description=tour_description,
            main_image=random.choice(images)  # Главное изображение
        )
        # Добавляем дополнительные изображения
        num_tour_images = random.randint(0, 2)
        for _ in range(num_tour_images):
            tour.images.add(random.choice(images))

        tours.append(tour)
        print(f"  Создан тур: {tour.title} (Цена: {tour.price}, Мест: {tour.available_slots})")
    if not tours:
        print("Не удалось создать туры. Прерываем заполнение.")
        return

    # 6. Бронирования
    bookings = []
    print("Создаем бронирования...")
    for i in range(25):  # Минимум 10 бронирований, создадим 25 для "популярности" туров
        user = random.choice(clients)
        tour = random.choice(tours)

        # Уменьшаем доступные места для тура при бронировании
        num_people = random.randint(1, 4)
        if tour.available_slots >= num_people:
            booking_status = random.choice(['pending', 'paid', 'confirmed', 'cancelled'])
            booking = Booking.objects.create(
                user=user,
                tour=tour,
                num_people=num_people,
                status=booking_status
            )
            bookings.append(booking)
            if booking_status in ['paid', 'confirmed']:
                # Уменьшаем только если бронирование подтверждено/оплачено
                tour.available_slots -= num_people
                tour.save()
            print(
                f"  Создано бронирование #{booking.id} для {user.username} на тур '{tour.title}' (Статус: {booking_status})")
        else:
            print(f"  Пропущено бронирование: недостаточно мест для тура '{tour.title}'")

    # 7. Отзывы
    reviews = []
    print("Создаем отзывы...")
    for i in range(30):  # Минимум 10 отзывов
        user = random.choice(clients)
        rating = random.randint(3, 5)
        text = f"Отличный сервис! Все очень понравилось. Оценка: {rating}/5. (Отзыв №{i + 1})"

        if random.random() > 0.5 and tours:  # Отзыв к туру
            review_tour = random.choice(tours)
            review = Review.objects.create(user=user, tour=review_tour, rating=rating, text=text)
            print(f"  Создан отзыв на тур '{review_tour.title}' от {user.username}")
        elif hotels:  # Отзыв к отелю
            review_hotel = random.choice(hotels)
            review = Review.objects.create(user=user, hotel=review_hotel, rating=rating, text=text)
            print(f"  Создан отзыв на отель '{review_hotel.name}' от {user.username}")
        else:
            print("  Не удалось создать отзыв: нет туров или отелей.")
            continue
        reviews.append(review)

    # 8. Акции
    promotions = []
    print("Создаем акции...")
    for i in range(10):  # Минимум 10 акций (активные и неактивные)
        promo_title = f"Супер акция {i + 1}!"
        promo_description = f"Невероятная скидка {random.randint(5, 25)}% на избранные направления!"

        # Акции: 70% активных, 30% неактивных
        if random.random() < 0.7:  # Активная акция
            start_date = today - timedelta(days=random.randint(0, 30))
            end_date = today + timedelta(days=random.randint(10, 60))
        else:  # Неактивная акция (прошлая или будущая)
            if random.random() < 0.5:  # Прошлая
                start_date = today - timedelta(days=random.randint(60, 90))
                end_date = today - timedelta(days=random.randint(10, 50))
            else:  # Будущая
                start_date = today + timedelta(days=random.randint(60, 90))
                end_date = start_date + timedelta(days=random.randint(10, 50))

        promotion = Promotion.objects.create(
            title=promo_title,
            description=promo_description,
            start_date=start_date,
            end_date=end_date
        )
        # Привязываем случайные туры и страны
        num_related_tours = random.randint(1, 5)
        promotion.tours.set(random.sample(tours, min(num_related_tours, len(tours))))
        num_related_countries = random.randint(1, 3)
        promotion.countries.set(random.sample(countries, min(num_related_countries, len(countries))))
        promotions.append(promotion)
        print(f"  Создана акция: '{promotion.title}' (Активна: {promotion.is_active})")

    # 9. Избранное
    favorites = []
    print("Создаем избранные туры...")
    for user in clients:
        # Каждый клиент добавит 1-3 случайных тура в избранное
        num_favorites = random.randint(1, 3)
        selected_tours = random.sample(tours, min(num_favorites, len(tours)))
        for tour in selected_tours:
            try:
                favorite, created = Favorite.objects.get_or_create(user=user, tour=tour)
                if created:
                    favorites.append(favorite)
                    print(f"  Тур '{tour.title}' добавлен в избранное для {user.username}")
            except Exception as e:
                # print(f"  Ошибка при добавлении в избранное (возможно, уже существует): {e}")
                pass  # Пропускаем, если запись уже существует

    print("\nЗаполнение базы данных завершено!")
    print(f"Всего пользователей: {User.objects.count()}")
    print(f"Всего стран: {Country.objects.count()}")
    print(f"Всего городов: {City.objects.count()}")
    print(f"Всего изображений: {Image.objects.count()}")
    print(f"Всего отелей: {Hotel.objects.count()}")
    print(f"Всего туров: {Tour.objects.count()}")
    print(f"Всего бронирований: {Booking.objects.count()}")
    print(f"Всего отзывов: {Review.objects.count()}")
    print(f"Всего акций: {Promotion.objects.count()}")
    print(f"Всего избранных туров: {Favorite.objects.count()}")


if __name__ == '__main__':
    # Эта часть выполнится только если скрипт запущен напрямую
    # Если запускаете через manage.py shell, то просто вызовите populate_database()
    populate_database()