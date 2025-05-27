# tours/views.py
from datetime import date

from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.shortcuts import render, get_object_or_404, redirect

from .forms import TourForm
from .models import Tour, Promotion, Country, City  # Добавили Hotel


def home_page(request):
    # 1. Виджет: Поиск туров (форма будет обрабатываться здесь или на отдельной странице)
    # На главной странице мы просто отображаем форму поиска.

    # 2. Виджет: Популярные/Рекомендуемые туры
    # Пример: Туры с наибольшим количеством бронирований или туры с высоким рейтингом
    # Здесь используем Count для агрегации
    popular_tours = Tour.objects.annotate(
        num_bookings=Count('bookings')
    ).order_by('-num_bookings', '-start_date')[:5]  # top-5 туров по количеству бронирований

    # Или, если хотим показать туры с хорошими отзывами:
    top_rated_tours = Tour.objects.annotate(
        avg_rating=Avg('reviews__rating')
    ).filter(avg_rating__gte=4).order_by('-avg_rating')[:5]  # top-5 туров с рейтингом >= 4

    # Выберем популярные туры для виджета
    featured_tours = popular_tours if popular_tours.exists() else Tour.objects.all().order_by('-start_date')[:5]

    # 3. Виджет: Акции и спецпредложения
    active_promotions = Promotion.objects.filter(
        start_date__lte=date.today(),
        end_date__gte=date.today()
    ).order_by('-start_date')[:3]  # top-3 активные акции

    # Дополнительные данные для формы поиска
    countries = Country.objects.all().order_by('name')
    cities = City.objects.all().order_by('name')  # Можно отфильтровать по стране через JS позже

    context = {
        'featured_tours': featured_tours,
        'active_promotions': active_promotions,
        'countries': countries,
        'cities': cities,
    }
    return render(request, 'tours/home.html', context)


def search_results(request):
    query = request.GET.get('q')
    country_id = request.GET.get('country')
    city_id = request.GET.get('city')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    tour_type = request.GET.get('tour_type')

    tours = Tour.objects.all()

    if query:
        tours = tours.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(country__name__icontains=query) |
            Q(city__name__icontains=query) |
            Q(hotel__name__icontains=query)
        )
    if country_id:
        tours = tours.filter(country_id=country_id)
    if city_id:
        tours = tours.filter(city_id=city_id)
    if start_date:
        tours = tours.filter(start_date__gte=start_date)
    if end_date:
        tours = tours.filter(end_date__lte=end_date)
    if min_price:
        tours = tours.filter(price__gte=min_price)
    if max_price:
        tours = tours.filter(price__lte=max_price)
    if tour_type and tour_type != 'all':
        tours = tours.filter(tour_type=tour_type)

    tours = tours.order_by('price', 'start_date')

    context = {
        'search_query': query,
        'tours': tours,
        'countries': Country.objects.all(),
        'cities': City.objects.all(),
        'tour_types': Tour.TOUR_TYPES,
        'selected_country': country_id,
        'selected_city': city_id,
        'selected_start_date': start_date,
        'selected_end_date': end_date,
        'selected_min_price': min_price,
        'selected_max_price': max_price,
        'selected_tour_type': tour_type,
    }
    return render(request, 'tours/search_results.html', context)


def tour_detail(request, tour_id):
    """Отображает детальную информацию о конкретном туре."""
    tour = get_object_or_404(Tour, pk=tour_id)

    # Получаем связанные объекты
    bookings = tour.bookings.all().order_by('-booking_date')[:5]  # Последние 5 бронирований
    reviews = tour.reviews.all().order_by('-created_at')  # Отзывы к туру

    # Пример агрегации для средней оценки
    # Измените эту строку:
    avg_rating_result = tour.reviews.aggregate(Avg('rating'))
    avg_rating = avg_rating_result['rating__avg'] if 'rating__avg' in avg_rating_result and avg_rating_result[
        'rating__avg'] is not None else None

    context = {
        'tour': tour,
        'bookings': bookings,
        'reviews': reviews,
        'avg_rating': avg_rating,  # Теперь avg_rating будет None, если нет отзывов
    }
    return render(request, 'tours/tour_detail.html', context)


def tour_add(request):
    """Страница для добавления нового тура."""
    if request.method == 'POST':
        form = TourForm(request.POST, request.FILES)
        if form.is_valid():
            tour = form.save(commit=False)

            # Если нужно сохранять Main Image, но не через форму ImageField напрямую
            # if 'main_image_file' in request.FILES:
            #     image_file = request.FILES['main_image_file']
            #     new_image = Image.objects.create(image=image_file, caption=f"Главное фото для {tour.title}")
            #     tour.main_image = new_image

            tour.save()
            # Обновление ManyToMany полей, если они есть и не в commit=False
            # form.save_m2m() # Если вы добавили Images в TourForm.Meta.fields

            messages.success(request, f"Тур '{tour.title}' успешно добавлен!")
            return redirect('tour_detail', tour_id=tour.pk)
        else:
            messages.error(request, "Ошибка при добавлении тура. Проверьте введенные данные.")
    else:
        form = TourForm()

    context = {
        'form': form,
        'form_title': "Добавить новый тур",
    }
    return render(request, 'tours/tour_form.html', context)


def tour_edit(request, tour_id):
    """Страница для редактирования существующего тура."""
    tour = get_object_or_404(Tour, pk=tour_id)
    if request.method == 'POST':
        form = TourForm(request.POST, request.FILES, instance=tour)
        if form.is_valid():
            tour = form.save(commit=False)
            # Логика для main_image_file, если реализовано в форме
            # if 'main_image_file' in request.FILES:
            #     image_file = request.FILES['main_image_file']
            #     if tour.main_image: # Удаляем старое изображение, если оно есть
            #         tour.main_image.image.delete(save=False) # Удаляем файл, но не объект из БД пока
            #         tour.main_image.delete() # Удаляем объект изображения из БД
            #     new_image = Image.objects.create(image=image_file, caption=f"Главное фото для {tour.title}")
            #     tour.main_image = new_image

            tour.save()
            # form.save_m2m() # Если вы добавили Images в TourForm.Meta.fields

            messages.success(request, f"Тур '{tour.title}' успешно обновлен!")
            return redirect('tour_detail', tour_id=tour.pk)
        else:
            messages.error(request, "Ошибка при редактировании тура. Проверьте введенные данные.")
    else:
        form = TourForm(instance=tour)

    context = {
        'form': form,
        'form_title': f"Редактировать тур: {tour.title}",
        'tour': tour,  # Передаем объект тура для ссылок
    }
    return render(request, 'tours/tour_form.html', context)


def tour_delete(request, tour_id):
    """Функция для удаления тура."""
    tour = get_object_or_404(Tour, pk=tour_id)
    if request.method == 'POST':
        tour_title = tour.title  # Сохраняем название до удаления
        tour.delete()
        messages.success(request, f"Тур '{tour_title}' успешно удален.")
        return redirect('home')  # Перенаправляем на главную после удаления

    # Если GET запрос, просто показываем страницу подтверждения
    context = {
        'tour': tour,
    }
    return render(request, 'tours/tour_confirm_delete.html', context)
