from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Country, City, Hotel, Tour, Booking, Review, Promotion, Favorite, Image

# Настройка Inline для связанных моделей
class BookingInline(admin.TabularInline):
    model = Booking
    extra = 0
    raw_id_fields = ('tour',)

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    raw_id_fields = ('tour', 'hotel',)

class FavoriteInline(admin.TabularInline):
    model = Favorite
    extra = 0
    raw_id_fields = ('tour',)

class ImageInline(admin.TabularInline):
    model = Tour.images.through # Для ManyToManyField
    extra = 0
    verbose_name = "Изображение для тура"
    verbose_name_plural = "Изображения для тура"
    raw_id_fields = ('image',) # Для удобства выбора изображений по ID

class HotelImageInline(admin.TabularInline):
    model = Hotel.images.through
    extra = 0
    verbose_name = "Изображение для отеля"
    verbose_name_plural = "Изображения для отеля"
    raw_id_fields = ('image',)


# Настройка User Admin
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'date_joined', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    inlines = [BookingInline, ReviewInline, FavoriteInline]


# Настройка Country Admin
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


# Настройка City Admin
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ('country',)
    search_fields = ('name', 'country__name')
    ordering = ('name',)


# Настройка Hotel Admin
@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'stars', 'city', 'country')
    list_filter = ('stars', 'city__country', 'city')
    search_fields = ('name', 'description', 'address', 'city__name', 'country__name')
    inlines = [HotelImageInline, ReviewInline]
    filter_horizontal = ('images',) # Для ManyToManyField
    raw_id_fields = ('country', 'city',) # Удобно для выбора страны и города по ID


# Настройка Tour Admin
@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('title', 'country', 'city', 'hotel', 'price', 'start_date', 'end_date', 'duration', 'available_slots', 'tour_type', 'get_is_active_display')
    list_display_links = ('title',) # Заголовок будет кликабельным
    list_filter = ('tour_type', 'country', 'city', 'start_date', 'end_date', 'available_slots', 'price', 'hotel__stars')
    search_fields = ('title', 'description', 'country__name', 'city__name', 'hotel__name')
    date_hierarchy = 'start_date' # Иерархия по дате начала
    ordering = ('-start_date',)
    readonly_fields = ('duration',) # Длительность можно сделать автоматически вычисляемой
    filter_horizontal = ('images',)
    raw_id_fields = ('country', 'city', 'hotel', 'main_image') # Для выбора связанных объектов по ID
    inlines = [BookingInline, ReviewInline]

    # Собственный метод для list_display
    @admin.display(description='Продолжительность (дней)')
    def get_duration_days(self, obj):
        return (obj.end_date - obj.start_date).days + 1

    def save_model(self, request, obj, form, change):
        # Автоматическое вычисление длительности
        if obj.start_date and obj.end_date:
            obj.duration = (obj.end_date - obj.start_date).days
        super().save_model(request, obj, form, change)


# Настройка Booking Admin
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'tour', 'booking_date', 'num_people', 'status', 'total_cost')
    list_display_links = ('id',)
    list_filter = ('status', 'booking_date', 'user', 'tour__country', 'tour__city')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'tour__title', 'status')
    date_hierarchy = 'booking_date'
    ordering = ('-booking_date',)
    raw_id_fields = ('user', 'tour') # Для выбора пользователя и тура по ID
    readonly_fields = ('booking_date',) # Дата бронирования устанавливается автоматически


# Настройка Review Admin
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_related_object', 'rating', 'created_at', 'text')
    list_filter = ('rating', 'created_at', 'user', 'tour__country', 'hotel__stars')
    search_fields = ('user__username', 'text', 'tour__title', 'hotel__name')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    raw_id_fields = ('user', 'tour', 'hotel')

    @admin.display(description='Объект отзыва')
    def get_related_object(self, obj):
        if obj.tour:
            return f"Тур: {obj.tour.title}"
        elif obj.hotel:
            return f"Отель: {obj.hotel.name}"
        return "Неизвестно"


# Настройка Promotion Admin
@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'get_is_active_display')
    list_filter = ('start_date', 'end_date')
    search_fields = ('title', 'description')
    date_hierarchy = 'start_date'
    filter_horizontal = ('tours', 'countries') # Для ManyToManyField


# Настройка Favorite Admin
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'tour', 'added_at')
    list_filter = ('added_at', 'user', 'tour__country', 'tour__city')
    search_fields = ('user__username', 'tour__title')
    date_hierarchy = 'added_at'
    raw_id_fields = ('user', 'tour') # Для выбора пользователя и тура по ID


# Настройка Image Admin
@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'caption', 'image')
    search_fields = ('caption',)
    readonly_fields = ('image_tag',) # Добавим метод для предпросмотра изображения

    from django.utils.html import mark_safe
    @admin.display(description='Предпросмотр изображения')
    def image_tag(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 150px; max-width: 150px;" />')
        return "Нет изображения"