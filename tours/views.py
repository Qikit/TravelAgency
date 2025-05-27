# tours/views.py
from django.shortcuts import render
from django.db.models import Count, Min, Max, Avg, Q
from datetime import date
from .models import Tour, Promotion, Review, Country, City

def home_page(request):
    # 1. Виджет: Поиск туров (форма будет обрабатываться здесь или на отдельной странице)
    # На главной странице мы просто отображаем форму поиска.

    # 2. Виджет: Популярные/Рекомендуемые туры
    # Пример: Туры с наибольшим количеством бронирований или туры с высоким рейтингом
    # Здесь используем Count для агрегации
    popular_tours = Tour.objects.annotate(
        num_bookings=Count('bookings')
    ).order_by('-num_bookings', '-start_date')[:5] # top-5 туров по количеству бронирований

    # Или, если хотим показать туры с хорошими отзывами:
    top_rated_tours = Tour.objects.annotate(
        avg_rating=Avg('reviews__rating')
    ).filter(avg_rating__gte=4).order_by('-avg_rating')[:5] # top-5 туров с рейтингом >= 4

    # Выберем популярные туры для виджета
    featured_tours = popular_tours if popular_tours.exists() else Tour.objects.all().order_by('-start_date')[:5]


    # 3. Виджет: Акции и спецпредложения
    active_promotions = Promotion.objects.filter(
        start_date__lte=date.today(),
        end_date__gte=date.today()
    ).order_by('-start_date')[:3] # top-3 активные акции

    # Дополнительные данные для формы поиска
    countries = Country.objects.all().order_by('name')
    cities = City.objects.all().order_by('name') # Можно отфильтровать по стране через JS позже

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