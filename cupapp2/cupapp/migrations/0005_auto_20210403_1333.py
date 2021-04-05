# Generated by Django 3.1.7 on 2021-04-03 13:33

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cupapp', '0004_auto_20190106_1255'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Cup',
            new_name='Tournament',
        ),
        migrations.AlterModelOptions(
            name='tournament',
            options={'ordering': ['-created']},
        ),
    ]
