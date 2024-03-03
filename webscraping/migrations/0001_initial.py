# Generated by Django 4.1.13 on 2024-03-03 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('authors', models.TextField(default='None', null=True)),
                ('publication_type', models.CharField(default='None', max_length=50, null=True)),
                ('publication_date', models.DateField(null=True)),
                ('publisher_name', models.CharField(default='None', max_length=100)),
                ('keywords_searched', models.TextField(default='None')),
                ('keywords_article', models.TextField(blank=True, default='None', null=True)),
                ('abstract', models.TextField(blank=True, null=True)),
                ('references', models.TextField(blank=True, default='None', null=True)),
                ('citation_count', models.IntegerField(blank=True, null=True)),
                ('doi_number', models.CharField(blank=True, max_length=50, null=True)),
                ('url', models.URLField(blank=True, null=True)),
                ('website_url', models.URLField(blank=True, null=True)),
            ],
        ),
    ]
