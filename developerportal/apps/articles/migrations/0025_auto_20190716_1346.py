# Generated by Django 2.2.3 on 2019-07-16 13:46

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.contrib.taggit
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ("taggit", "0002_auto_20150616_2121"),
        ("articles", "0024_auto_20190711_1222"),
    ]

    operations = [
        migrations.CreateModel(
            name="ArticlesTag",
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
                    "content_object",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tagged_items",
                        to="articles.Articles",
                    ),
                ),
                (
                    "tag",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="articles_articlestag_items",
                        to="taggit.Tag",
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.AddField(
            model_name="articles",
            name="keywords",
            field=modelcluster.contrib.taggit.ClusterTaggableManager(
                blank=True,
                help_text="A comma-separated list of tags.",
                through="articles.ArticlesTag",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
        ),
    ]
