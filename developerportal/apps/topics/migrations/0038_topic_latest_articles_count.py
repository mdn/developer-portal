# Generated by Django 2.2.3 on 2019-08-01 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("topics", "0037_auto_20190730_1057")]

    operations = [
        migrations.AddField(
            model_name="topic",
            name="latest_articles_count",
            field=models.IntegerField(
                choices=[(3, "3"), (6, "6"), (9, "9")], default=3
            ),
        )
    ]
