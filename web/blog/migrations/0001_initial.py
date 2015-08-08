# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=250, help_text='Maximum 250 characters.')),
                ('slug', models.SlugField(unique=True, help_text='Suggested value automatically generated from title. Must be unique.')),
                ('description', models.TextField()),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=250)),
                ('excerpt', models.TextField(blank=True)),
                ('body', models.TextField()),
                ('published_on', models.DateField(default=datetime.date.today)),
                ('excerpt_html', models.TextField(editable=False, blank=True)),
                ('body_html', models.TextField(editable=False, blank=True)),
                ('enable_comments', models.BooleanField(default=True)),
                ('featured', models.BooleanField(default=False)),
                ('slug', models.SlugField(unique_for_date='published_on')),
                ('status', models.IntegerField(choices=[(1, 'Live'), (2, 'Draft'), (3, 'Hidden')], default=2)),
                ('categories', models.ManyToManyField(to='blog.Category', related_name='entries')),
                ('tags', taggit.managers.TaggableManager(verbose_name='Tags', to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.')),
            ],
            options={
                'verbose_name': 'Entry',
                'verbose_name_plural': 'Entries',
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50)),
                ('prism_tag', models.CharField(max_length=50, verbose_name='PRISM Tag')),
            ],
            options={
                'verbose_name': 'Language',
                'verbose_name_plural': 'Languages',
            },
        ),
        migrations.CreateModel(
            name='Snippet',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(unique=True, blank=True, help_text='Will be generated if left blank.')),
                ('code', models.TextField()),
                ('entry', models.ForeignKey(to='blog.Entry', related_name='snippets')),
                ('language', models.ForeignKey(to='blog.Language', related_name='snippets')),
            ],
            options={
                'verbose_name': 'Snippet',
                'verbose_name_plural': 'Snippets',
            },
        ),
        migrations.CreateModel(
            name='TagColor',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tag_name', models.CharField(max_length=50, unique=True, verbose_name='Tag Name')),
                ('color_hex', models.CharField(max_length=6, verbose_name='Color Hex')),
                ('text_color', models.CharField(max_length=6, verbose_name='Text Color', blank=True, default='fff')),
            ],
            options={
                'verbose_name': 'Tag Color',
                'verbose_name_plural': 'Tag Colors',
            },
        ),
    ]
