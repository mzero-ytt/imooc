# Generated by Django 2.0.1 on 2018-01-16 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0004_courseorg_teacher'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseorg',
            name='course_nums',
            field=models.IntegerField(default=0, verbose_name='课程数'),
        ),
    ]
