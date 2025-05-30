# Generated by Django 5.2.1 on 2025-05-29 23:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tours', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tour',
            name='available_slots',
            field=models.IntegerField(verbose_name='Доступные места'),
        ),
        migrations.AlterField(
            model_name='tour',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tours.city', verbose_name='Город'),
        ),
        migrations.AlterField(
            model_name='tour',
            name='country',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tours.country', verbose_name='Страна'),
        ),
        migrations.AlterField(
            model_name='tour',
            name='description',
            field=models.TextField(default='', verbose_name='Описание тура'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tour',
            name='duration',
            field=models.IntegerField(verbose_name='Продолжительность (дни)'),
        ),
        migrations.AlterField(
            model_name='tour',
            name='hotel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tours.hotel', verbose_name='Отель'),
        ),
        migrations.AlterField(
            model_name='tour',
            name='images',
            field=models.ManyToManyField(blank=True, related_name='tours_gallery', to='tours.image', verbose_name='Галерея изображений'),
        ),
        migrations.AlterField(
            model_name='tour',
            name='main_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tours_main_image', to='tours.image', verbose_name='Главное изображение'),
        ),
        migrations.AlterField(
            model_name='tour',
            name='title',
            field=models.CharField(max_length=200, verbose_name='Название тура'),
        ),
        migrations.AlterField(
            model_name='tour',
            name='tour_type',
            field=models.CharField(choices=[('beach', 'Пляжный отдых'), ('excursion', 'Экскурсионный'), ('adventure', 'Приключения'), ('ski', 'Горнолыжный'), ('cruise', 'Круиз'), ('medical', 'Оздоровительный'), ('business', 'Деловой'), ('other', 'Другое')], default='other', max_length=50, verbose_name='Тип тура'),
        ),
    ]
