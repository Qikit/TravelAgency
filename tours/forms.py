# tours/forms.py
from django import forms
from .models import Tour, Image, Country, City, Hotel

class TourForm(forms.ModelForm):
    # Добавляем поля, которые пользователь будет редактировать/заполнять
    # Если поля ForeignKey, Django автоматически создаст для них Select/ChoiceField
    country = forms.ModelChoiceField(queryset=Country.objects.all().order_by('name'), label="Страна")
    city = forms.ModelChoiceField(queryset=City.objects.all().order_by('name'), label="Город")
    hotel = forms.ModelChoiceField(queryset=Hotel.objects.all().order_by('name'), label="Отель", required=False) # Отель может быть необязательным

    # Можно добавить поле для загрузки главной картинки прямо здесь
    # main_image_file = forms.ImageField(label="Главное изображение (загрузить)", required=False)


    class Meta:
        model = Tour
        fields = [
            'title',
            'country',
            'city',
            'hotel',
            'price',
            'start_date',
            'end_date',
            'tour_type',
            'description',
            # 'main_image', # Если вы хотите выбирать из существующих картинок
            # 'images',     # Если вы хотите выбирать из существующих картинок для ManyToMany
        ]
        # Используем виджеты для дат, чтобы в браузере был календарь
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'title': "Название тура",
            'price': "Цена",
            'start_date': "Дата начала",
            'end_date': "Дата окончания",
            'tour_type': "Тип тура",
            'description': "Описание",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Динамическая подгрузка городов в зависимости от выбранной страны (позже можно добавить JS)
        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['city'].queryset = City.objects.filter(country_id=country_id).order_by('name')
                self.fields['hotel'].queryset = Hotel.objects.filter(country_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk: # Если это редактирование существующего тура
            self.fields['city'].queryset = City.objects.filter(country=self.instance.country).order_by('name')
            self.fields['hotel'].queryset = Hotel.objects.filter(country=self.instance.country).order_by('name')
        else: # При добавлении нового тура, по умолчанию городов и отелей нет
            self.fields['city'].queryset = City.objects.none()
            self.fields['hotel'].queryset = Hotel.objects.none()

        # Добавляем классы Bootstrap для стилизации
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.Select, forms.DateInput, forms.NumberInput)):
                field.widget.attrs['class'] = 'form-control'
            elif isinstance(field.widget, forms.CheckboxInput):
                 field.widget.attrs['class'] = 'form-check-input'