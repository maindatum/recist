# Generated by Django 3.0.3 on 2020-03-13 06:12

import chemoresponse.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EvalModality',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modality_type', models.CharField(choices=[('CT', 'CT'), ('MRI', 'MRI'), ('PET', 'PET'), ('USO', 'US')], max_length=3)),
                ('body_field', models.CharField(choices=[('HEO', 'Head/Orbit/PNS'), ('NEC', 'Neck'), ('BRA', 'Brain'), ('CHE', 'Chest'), ('APE', 'Abd/Pel'), ('SPI', 'Spine')], max_length=10)),
                ('image_date', models.DateField()),
                ('saved_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unitnumb', models.IntegerField()),
                ('ptname', models.CharField(max_length=16)),
                ('regist_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='TumorTarget',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target_no', models.IntegerField()),
                ('votes', models.IntegerField(default=0)),
                ('target_yn', models.BooleanField(default=False, verbose_name='target lesion Y/N')),
                ('nontarget_yn', models.BooleanField(default=False, verbose_name='Non Target Y/N')),
                ('reference_yn', models.BooleanField(default=False, verbose_name='reference Y/N')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemoresponse.Patient')),
            ],
        ),
        migrations.CreateModel(
            name='TargetImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target_image', chemoresponse.fields.ImageWithThumbField(null=True, upload_to='target_image')),
                ('image_desc', models.TextField()),
                ('image_date', models.DateField()),
                ('saved_date', models.DateTimeField(auto_now_add=True)),
                ('image_modal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemoresponse.EvalModality')),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemoresponse.TumorTarget')),
            ],
        ),
        migrations.AddField(
            model_name='evalmodality',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chemoresponse.Patient'),
        ),
    ]
