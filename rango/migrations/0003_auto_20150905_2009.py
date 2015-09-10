# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from django.template.defaultfilters import slugify

def create_category_slug(apps, schema_editor):
        Category = apps.get_model("rango", "Category")
        for category in Category.objects.all():
                category.slug = slugify(category.name)
                category.save()

class Migration(migrations.Migration):

    dependencies = [
        ('rango', '0002_category_slug'),
    ]

    operations = [
	migrations.RunPython(create_category_slug),
    ]
