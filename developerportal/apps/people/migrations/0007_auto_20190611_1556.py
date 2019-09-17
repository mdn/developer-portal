# Generated by Django 2.2.1 on 2019-06-11 15:56

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ("topics", "0007_auto_20190611_1542"),
        ("people", "0006_auto_20190604_1050"),
    ]

    operations = [
        migrations.RemoveField(model_name="person", name="topics"),
        migrations.CreateModel(
            name="PersonTopic",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sort_order",
                    models.IntegerField(blank=True, editable=False, null=True),
                ),
                (
                    "person",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="topics",
                        to="people.Person",
                    ),
                ),
                (
                    "topic",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="topics.Topic",
                    ),
                ),
            ],
            options={"ordering": ["sort_order"], "abstract": False},
        ),
    ]
