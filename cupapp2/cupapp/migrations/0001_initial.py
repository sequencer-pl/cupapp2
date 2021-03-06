# Generated by Django 2.1.3 on 2018-11-21 23:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cups',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('description', models.CharField(max_length=256)),
                ('form', models.CharField(choices=[('cup', 'cup'), ('league', 'league')], max_length=64)),
                ('created', models.DateTimeField(auto_now=True)),
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FixturePlayers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('home_away_indicator', models.CharField(choices=[('H', 'home'), ('A', 'away')], max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Fixtures',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cupapp.Cups')),
            ],
        ),
        migrations.CreateModel(
            name='Players',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('stars_handicap', models.SmallIntegerField(default=10)),
                ('cup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cupapp.Cups')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='fixtureplayers',
            name='fixture',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cupapp.Fixtures'),
        ),
        migrations.AddField(
            model_name='fixtureplayers',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cupapp.Players'),
        ),
    ]
