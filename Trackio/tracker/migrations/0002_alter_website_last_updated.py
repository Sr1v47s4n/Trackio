# Generated by Django 4.2.10 on 2024-07-20 05:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tracker", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="website",
            name="last_updated",
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
