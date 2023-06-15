# Generated by Django 4.2 on 2023-05-25 08:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0006_contact_message_contacts"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="contact",
            name="first_name",
        ),
        migrations.RemoveField(
            model_name="contact",
            name="last_name",
        ),
        migrations.AddField(
            model_name="contact",
            name="name",
            field=models.CharField(blank=True, max_length=96, null=True),
        ),
    ]
