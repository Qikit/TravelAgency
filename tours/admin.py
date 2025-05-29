from django.contrib import admin
from .models import User, Country, City, Hotel, Image, Tour, Booking, Review, Promotion, Favorite
from datetime import date

class TourImageInline(admin.TabularInline):
    model = Tour.images.through
    extra = 1

class HotelImageInline(admin.TabularInline):
    model = Hotel.images.through
    extra = 1

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone', 'role', 'date_registered', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone')
    ordering = ('-date_registered',)

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ('country',)
    search_fields = ('name', 'country__name')

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'stars', 'city', 'country')
    list_filter = ('stars', 'country', 'city')
    search_fields = ('name', 'address', 'city__name', 'country__name')
    inlines = [HotelImageInline]

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('title', 'country', 'city', 'price', 'start_date', 'end_date', 'available_slots', 'tour_type', 'is_tour_active')
    list_filter = ('tour_type', 'country', 'city', 'start_date', 'end_date')
    search_fields = ('title', 'description', 'country__name', 'city__name', 'hotel__name')
    date_hierarchy = 'start_date'
    raw_id_fields = ('hotel', 'main_image')
    inlines = [TourImageInline]

    @admin.display(description='Активен', boolean=True)
    def is_tour_active(self, obj):
        return obj.is_active()

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'tour', 'num_people', 'status', 'booking_date', 'get_total_cost')
    list_filter = ('status', 'booking_date')
    search_fields = ('user__username', 'tour__title')
    raw_id_fields = ('user', 'tour')
    date_hierarchy = 'booking_date'

    @admin.display(description='Общая стоимость')
    def get_total_cost(self, obj):
        return obj.tour.price * obj.num_people

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'tour', 'hotel', 'rating', 'created_at')
    list_filter = ('rating', 'tour', 'hotel')
    search_fields = ('user__username', 'tour__title', 'hotel__name', 'text')
    raw_id_fields = ('user', 'tour', 'hotel')

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'get_is_active_display')
    list_filter = ('start_date', 'end_date')
    search_fields = ('title', 'description')
    date_hierarchy = 'start_date'

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'tour', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'tour__title')
    raw_id_fields = ('user', 'tour')

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('caption', 'image')
    search_fields = ('caption', 'image')