from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Tour, Country, City, Promotion, Review, Booking
from .forms import TourForm
from django.db.models import Avg, Count
from datetime import date

def home_page(request):
    countries = Country.objects.all().order_by('name')
    cities = City.objects.all().order_by('name')
    TOUR_TYPES = Tour.TOUR_TYPES
    featured_tours = Tour.objects.filter(available_slots__gt=0, end_date__gte=date.today()).annotate(booking_count=Count('bookings')).order_by('-booking_count', '-start_date')[:6]
    active_promotions = Promotion.objects.filter(start_date__lte=date.today(), end_date__gte=date.today()).order_by('-start_date')[:3]

    context = {
        'countries': countries,
        'cities': cities,
        'TOUR_TYPES': TOUR_TYPES,
        'featured_tours': featured_tours,
        'active_promotions': active_promotions,
    }
    return render(request, 'tours/home.html', context)

def search_results(request):
    country_id = request.GET.get('country')
    city_id = request.GET.get('city')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    tour_type = request.GET.get('tour_type')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    tours = Tour.objects.filter(available_slots__gt=0, end_date__gte=date.today()).order_by('start_date')

    if country_id:
        tours = tours.filter(country__id=country_id)
    if city_id:
        tours = tours.filter(city__id=city_id)
    if start_date:
        tours = tours.filter(start_date__gte=start_date)
    if end_date:
        tours = tours.filter(end_date__lte=end_date)
    if tour_type and tour_type != 'all':
        tours = tours.filter(tour_type=tour_type)
    if min_price:
        tours = tours.filter(price__gte=min_price)
    if max_price:
        tours = tours.filter(price__lte=max_price)

    countries = Country.objects.all().order_by('name')
    cities = City.objects.all().order_by('name')
    TOUR_TYPES = Tour.TOUR_TYPES

    context = {
        'tours': tours,
        'countries': countries,
        'cities': cities,
        'TOUR_TYPES': TOUR_TYPES,
        'selected_country': country_id,
        'selected_city': city_id,
        'selected_start_date': start_date,
        'selected_end_date': end_date,
        'selected_tour_type': tour_type,
        'selected_min_price': min_price,
        'selected_max_price': max_price,
    }
    return render(request, 'tours/search_results.html', context)

def tour_detail(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    reviews = Review.objects.filter(tour=tour).order_by('-created_at')
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    bookings = Booking.objects.filter(tour=tour).order_by('-booking_date')[:5]

    context = {
        'tour': tour,
        'reviews': reviews,
        'average_rating': average_rating,
        'bookings': bookings,
    }
    return render(request, 'tours/tour_detail.html', context)

def tour_add(request):
    if request.method == 'POST':
        form = TourForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Тур успешно добавлен!')
            return redirect('home')
        else:
            messages.error(request, 'Ошибка при добавлении тура. Проверьте введенные данные.')
    else:
        form = TourForm()
    return render(request, 'tours/tour_form.html', {'form': form, 'page_title': 'Добавить новый тур'})

def tour_edit(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    if request.method == 'POST':
        form = TourForm(request.POST, request.FILES, instance=tour)
        if form.is_valid():
            form.save()
            messages.success(request, 'Тур успешно обновлен!')
            return redirect('tour_detail', tour_id=tour.pk)
        else:
            messages.error(request, 'Ошибка при обновлении тура. Проверьте введенные данные.')
    else:
        form = TourForm(instance=tour)
    return render(request, 'tours/tour_form.html', {'form': form, 'tour': tour, 'page_title': 'Редактировать тур'})

def tour_delete(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    if request.method == 'POST':
        tour.delete()
        messages.success(request, 'Тур успешно удален.')
        return redirect('home')
    return render(request, 'tours/tour_confirm_delete.html', {'tour': tour})