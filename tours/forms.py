from django import forms
from .models import Tour, Image, Country, City, Hotel


class TourForm(forms.ModelForm):
    new_main_image = forms.ImageField(required=False, label='Загрузить новое главное изображение')

    country = forms.ModelChoiceField(queryset=Country.objects.all().order_by('name'), label="Страна")
    city = forms.ModelChoiceField(queryset=City.objects.all().order_by('name'), label="Город")
    hotel = forms.ModelChoiceField(queryset=Hotel.objects.all().order_by('name'), label="Отель", required=False)

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
            'duration',
            'available_slots',
            'tour_type',
            'description',
            'main_image'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['city'].queryset = City.objects.filter(country_id=country_id).order_by('name')
                self.fields['hotel'].queryset = Hotel.objects.filter(country_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['city'].queryset = City.objects.filter(country=self.instance.country).order_by('name')
            self.fields['hotel'].queryset = Hotel.objects.filter(country=self.instance.country).order_by('name')
        else:
            self.fields['city'].queryset = City.objects.none()
            self.fields['hotel'].queryset = Hotel.objects.none()

        for field_name in ['country', 'city', 'hotel', 'tour_type', 'main_image']:
            self.fields[field_name].widget.attrs['class'] = 'form-select'

        for field_name in ['title', 'price', 'start_date', 'end_date', 'duration', 'available_slots', 'description',
                           'new_main_image']:
            self.fields[field_name].widget.attrs['class'] = 'form-control'

        if self.instance and self.instance.main_image:
            self.fields['main_image'].label = f"Текущее главное изображение: {self.instance.main_image.image.name}"

    def clean(self):
        cleaned_data = super().clean()
        new_image_file = cleaned_data.get('new_main_image')

        if new_image_file:
            image_obj = Image.objects.create(image=new_image_file)
            cleaned_data['main_image'] = image_obj

        return cleaned_data