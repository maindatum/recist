# Generated by Django 3.0.3 on 2020-03-13 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chemoresponse', '0002_targetimage_baseline'),
    ]

    operations = [
        migrations.AddField(
            model_name='targetimage',
            name='lesion_measure',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=6, verbose_name='Measure'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='targetimage',
            name='image_date',
            field=models.DateField(blank=True),
        ),
        migrations.AlterField(
            model_name='targetimage',
            name='image_desc',
            field=models.TextField(blank=True, verbose_name='특기사항'),
        ),
    ]
