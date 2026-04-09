"""Add search_vector field and GIN indexes for extra_data, reproducibility, search_vector."""

import django.contrib.postgres.search
from django.contrib.postgres.indexes import GinIndex
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="contentitem",
            name="search_vector",
            field=django.contrib.postgres.search.SearchVectorField(
                blank=True, null=True
            ),
        ),
        migrations.AddIndex(
            model_name="contentitem",
            index=GinIndex(fields=["extra_data"], name="idx_ci_extra"),
        ),
        migrations.AddIndex(
            model_name="contentitem",
            index=GinIndex(fields=["reproducibility"], name="idx_ci_repro"),
        ),
        migrations.AddIndex(
            model_name="contentitem",
            index=GinIndex(fields=["search_vector"], name="idx_ci_fts"),
        ),
    ]
