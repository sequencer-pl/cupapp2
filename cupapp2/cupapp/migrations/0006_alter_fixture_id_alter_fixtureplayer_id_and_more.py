# Generated by Django 4.0 on 2022-01-03 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cupapp', '0005_auto_20210403_1333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fixture',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='fixtureplayer',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='player',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='tournament',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
