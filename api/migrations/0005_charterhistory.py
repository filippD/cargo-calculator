# Generated by Django 4.1 on 2023-09-01 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_usersession_session_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='CharterHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_of_flights', models.IntegerField(default=0)),
                ('departure_city', models.CharField(max_length=255)),
                ('arrival_city', models.CharField(max_length=255)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['created_on'],
            },
        ),
    ]
