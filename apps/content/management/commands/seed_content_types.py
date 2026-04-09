"""Management command to seed content types, tags, superuser, and sample content."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.content.models import (
    ContentItem,
    ContentRelation,
    ContentSourceLink,
    ContentTypeDef,
    SourceReference,
)
from apps.taxonomy.models import ContentTag, Tag


CONTENT_TYPES = [
    {
        "slug": "data_format",
        "name": "Data Format",
        "description": "Scientific data file formats (NetCDF, HDF5, Zarr, etc.)",
        "template_name": "content/data_format_detail.html",
        "icon_slug": "data-format",
        "sort_order": 1,
    },
    {
        "slug": "software_tool",
        "name": "Software Tool",
        "description": "Libraries and tools for reading, writing, and processing scientific data",
        "template_name": "content/software_tool_detail.html",
        "icon_slug": "software-tool",
        "sort_order": 2,
    },
    {
        "slug": "data_source",
        "name": "Data Repository",
        "description": "Scientific data repositories and archives",
        "template_name": "content/data_source_detail.html",
        "icon_slug": "data-source",
        "sort_order": 3,
    },
    {
        "slug": "workflow",
        "name": "Workflow / Recipe",
        "description": "Step-by-step guides for common scientific data tasks",
        "template_name": "content/workflow_detail.html",
        "icon_slug": "workflow",
        "sort_order": 4,
    },
    {
        "slug": "concept_guide",
        "name": "Concept Guide",
        "description": "Explanations of key concepts in scientific data management",
        "template_name": "content/concept_guide_detail.html",
        "icon_slug": "concept-guide",
        "sort_order": 5,
    },
]

TAGS = {
    "domain": [
        "climate", "atmospheric-science", "oceanography", "hydrology",
        "geophysics", "genomics", "astrophysics", "materials-science",
        "high-energy-physics", "neuroscience", "medical-imaging",
    ],
    "format": [
        "netcdf", "hdf5", "zarr", "grib", "fits", "fastq", "bam",
        "dicom", "parquet", "arrow", "csv", "json-ld", "geotiff",
    ],
    "language": [
        "python", "r", "julia", "fortran", "c-cpp", "matlab", "bash",
    ],
    "skill": [
        "beginner", "intermediate", "advanced",
    ],
    "topic": [
        "parallel-io", "format-conversion", "cloud-storage", "ai-readiness",
        "provenance", "metadata-standards", "visualization", "compression",
        "version-control", "data-citation", "performance-tuning",
        "data-validation", "anonymization", "leakage-prevention",
    ],
}

_DRAFT_07 = "http://json-schema.org/draft-07/schema#"

EXTRA_SCHEMAS = {
    "data_format": {
        "$schema": _DRAFT_07,
        "type": "object",
        "additionalProperties": True,
        "properties": {
            "canonical_name": {"type": "string"},
            "aliases": {"type": "array", "items": {"type": "string"}},
            "domains": {"type": "array", "items": {"type": "string"}},
            "file_extensions": {"type": "array", "items": {"type": "string"}},
            "mime_types": {"type": "array", "items": {"type": "string"}},
            "specification_url": {"type": "string", "format": "uri"},
            "structure_description": {"type": "string"},
            "common_use_cases": {"type": "array", "items": {"type": "string"}},
            "strengths": {"type": "array", "items": {"type": "string"}},
            "limitations": {"type": "array", "items": {"type": "string"}},
            "validation_methods": {"type": "array", "items": {"type": "string"}},
            "conversion_paths": {"type": "array", "items": {"type": "string"}},
            "ai_readiness_notes": {"type": "string"},
            "security_privacy_notes": {"type": "string"},
            "is_binary": {"type": "boolean"},
            "is_self_describing": {"type": "boolean"},
            "supports_parallel_io": {"type": "boolean"},
            "cloud_optimized": {"type": "boolean"},
        },
    },
    "software_tool": {
        "$schema": _DRAFT_07,
        "type": "object",
        "additionalProperties": True,
        "properties": {
            "official_site": {"type": "string", "format": "uri"},
            "repository_url": {"type": "string", "format": "uri"},
            "programming_language": {"type": "string"},
            "installation_methods": {"type": "array", "items": {"type": "string"}},
            "supported_formats": {"type": "array", "items": {"type": "string"}},
            "platform_support": {"type": "array", "items": {"type": "string"}},
            "license": {"type": "string"},
            "quick_start": {"type": "string"},
            "known_issues": {"type": "string"},
        },
    },
    "data_source": {
        "$schema": _DRAFT_07,
        "type": "object",
        "additionalProperties": True,
        "properties": {
            "host_organization": {"type": "string"},
            "access_model": {"type": "string"},
            "api_available": {"type": "boolean"},
            "authentication_required": {"type": "boolean"},
            "license_options": {"type": "array", "items": {"type": "string"}},
            "metadata_schema": {"type": "string"},
            "identifier_system": {"type": "string"},
            "sample_query": {"type": "string"},
            "rate_limits": {"type": "string"},
            "download_methods": {"type": "array", "items": {"type": "string"}},
            "data_domains": {"type": "array", "items": {"type": "string"}},
            "size_estimate": {"type": "string"},
        },
    },
    "workflow": {
        "$schema": _DRAFT_07,
        "type": "object",
        "additionalProperties": True,
        "properties": {
            "problem_statement": {"type": "string"},
            "skill_level": {"type": "string"},
            "estimated_minutes": {"type": "integer"},
            "inputs": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "format": {"type": "string"},
                        "size_hint": {"type": "string"},
                    },
                },
            },
            "tools_required": {"type": "array", "items": {"type": "string"}},
            "steps_summary": {"type": "array", "items": {"type": "string"}},
            "code_language": {"type": "string"},
            "expected_output_summary": {"type": "string"},
            "common_errors": {"type": "array", "items": {"type": "string"}},
            "tested_on": {
                "type": "object",
                "properties": {
                    "python": {"type": "string"},
                    "packages": {"type": "object"},
                },
            },
        },
    },
    "concept_guide": {
        "$schema": _DRAFT_07,
        "type": "object",
        "additionalProperties": True,
        "properties": {
            "skill_level": {"type": "string"},
            "related_formats": {"type": "array", "items": {"type": "string"}},
            "related_tools": {"type": "array", "items": {"type": "string"}},
            "key_terms": {"type": "array", "items": {"type": "string"}},
            "further_reading_dois": {"type": "array", "items": {"type": "string"}},
        },
    },
}

SEED_ITEMS = [
    {
        "slug": "netcdf-4",
        "content_type_slug": "data_format",
        "title": "NetCDF-4",
        "body_md": (
            "## Overview\n\n"
            "NetCDF-4 (Network Common Data Form version 4) is the current generation of "
            "the [NetCDF](https://www.unidata.ucar.edu/software/netcdf/) data format, "
            "built on top of HDF5. It is the de facto standard for storing array-oriented "
            "scientific data in climate science, oceanography, and atmospheric research.\n\n"
            "## Key Features\n\n"
            "NetCDF-4 is **self-describing**: every file embeds dimension names, variable "
            "attributes, and coordinate metadata so consumers never need a separate schema "
            "file. It supports chunked storage and internal compression (zlib, szip), "
            "making it practical for multi-terabyte datasets.\n\n"
            "```python\n"
            "import xarray as xr\n\n"
            "# Open a NetCDF-4 file with lazy loading\n"
            "ds = xr.open_dataset('tas_day_CESM2_historical.nc', chunks={'time': 365})\n"
            "print(ds)\n"
            "```\n\n"
            "## Considerations\n\n"
            "While NetCDF-4 excels for on-premises HPC workflows with parallel I/O via "
            "MPI, it is **not cloud-optimized** out of the box. For cloud-native access "
            "patterns, consider converting to [Zarr](/content/zarr/) using the workflow "
            "described in [NetCDF to Zarr Conversion](/content/netcdf-to-zarr-workflow/)."
        ),
        "extra_data": {
            "canonical_name": "NetCDF-4",
            "aliases": ["netcdf4", "nc4"],
            "domains": ["climate", "oceanography"],
            "file_extensions": [".nc", ".nc4"],
            "mime_types": ["application/x-netcdf"],
            "specification_url": "https://www.unidata.ucar.edu/software/netcdf/",
            "structure_description": "HDF5-based, self-describing, array-oriented",
            "common_use_cases": [
                "model output", "reanalysis", "observational gridded data",
            ],
            "strengths": ["self-describing", "parallel I/O", "compression"],
            "limitations": ["complex API", "large overhead for small files"],
            "validation_methods": ["ncdump -h", "cf-checker"],
            "conversion_paths": ["zarr", "parquet"],
            "ai_readiness_notes": (
                "Irregular grids need regridding; use cf_xarray for CF standard names"
            ),
            "security_privacy_notes": (
                "Global attributes may embed author personal info "
                "— verify before sharing"
            ),
            "is_binary": True,
            "is_self_describing": True,
            "supports_parallel_io": True,
            "cloud_optimized": False,
        },
        "reproducibility": {
            "level": "documented",
            "tested_with": [
                {"tool": "ncdump", "version": "4.9.2"},
                {"tool": "xarray", "version": "2024.10.0"},
            ],
            "tested_on_os": "Ubuntu 22.04 LTS",
            "limitations": "Format description; no runnable code.",
            "last_verified_at": "2025-03-15",
        },
        "status": "published",
        "visibility": "public",
    },
    {
        "slug": "xarray",
        "content_type_slug": "software_tool",
        "title": "xarray",
        "body_md": (
            "## Overview\n\n"
            "[xarray](https://docs.xarray.dev) is the leading Python library for working "
            "with labelled multi-dimensional arrays. It brings the power of "
            "[pandas](https://pandas.pydata.org/) to N-dimensional data, making it "
            "indispensable for climate, weather, and geoscience workflows.\n\n"
            "## Quick Start\n\n"
            "```python\n"
            "import xarray as xr\n\n"
            "# Open a NetCDF-4 dataset with chunked (lazy) loading\n"
            "ds = xr.open_dataset('temperature.nc', chunks={'time': 100})\n\n"
            "# Select a variable, slice by coordinate, compute mean\n"
            "tas = ds['tas'].sel(lat=slice(-30, 30))\n"
            "annual_mean = tas.groupby('time.year').mean('time')\n"
            "annual_mean.plot()\n"
            "```\n\n"
            "## Chunked Computation with Dask\n\n"
            "When you open a dataset with `chunks=`, xarray delegates computation to "
            "[Dask](https://dask.org), enabling out-of-core and parallel processing:\n\n"
            "```python\n"
            "# Compute global mean temperature — runs in parallel\n"
            "global_mean = ds['tas'].mean(dim=['lat', 'lon']).compute()\n"
            "```\n\n"
            "This pattern is essential when working with datasets that exceed available "
            "RAM. See the [Chunked I/O concept guide](/content/chunked-io-concept/) for "
            "a deeper explanation."
        ),
        "extra_data": {
            "official_site": "https://docs.xarray.dev",
            "repository_url": "https://github.com/pydata/xarray",
            "programming_language": "Python",
            "installation_methods": [
                "pip install xarray",
                "conda install -c conda-forge xarray",
            ],
            "supported_formats": ["netcdf", "zarr", "hdf5"],
            "platform_support": ["Linux", "macOS", "Windows"],
            "license": "Apache-2.0",
            "quick_start": "import xarray as xr\nds = xr.open_dataset('file.nc')",
            "known_issues": (
                "Large files exhaust memory without chunking "
                "— use chunks= argument"
            ),
        },
        "reproducibility": {
            "level": "documented",
            "tested_with": [
                {"tool": "Python", "version": "3.12.1"},
                {"tool": "xarray", "version": "2024.10.0"},
            ],
            "tested_on_os": "Ubuntu 22.04 LTS",
            "limitations": "Tool description; code snippets tested manually.",
            "last_verified_at": "2025-03-15",
        },
        "status": "published",
        "visibility": "public",
    },
    {
        "slug": "ncar-rda",
        "content_type_slug": "data_source",
        "title": "NCAR Research Data Archive",
        "body_md": (
            "## Overview\n\n"
            "The [NCAR Research Data Archive](https://rda.ucar.edu/) (RDA) is one of the "
            "world's largest collections of meteorological and oceanographic observations "
            "and model output, managed by the National Center for Atmospheric Research. "
            "It holds over 5 PB of data spanning decades of climate records.\n\n"
            "## Access Methods\n\n"
            "The RDA supports multiple download methods to accommodate different "
            "workflows:\n\n"
            "- **HTTP** — Direct file download via browser or `wget`/`curl`\n"
            "- **Globus** — High-speed, fault-tolerant transfer for large datasets\n"
            "- **OPeNDAP** — Server-side subsetting; retrieve only the variables and "
            "spatial/temporal slices you need\n\n"
            "```python\n"
            "import xarray as xr\n\n"
            "# Access an RDA dataset via OPeNDAP (requires authentication)\n"
            "url = 'https://rda.ucar.edu/thredds/dodsC/ds083.2/2024/ei.oper.an.pl.nc'\n"
            "ds = xr.open_dataset(url)\n"
            "```\n\n"
            "## Authentication\n\n"
            "Most datasets require a free NCAR RDA account. API access is rate-limited "
            "to 100 requests/hour for anonymous users and 1000 for authenticated users."
        ),
        "extra_data": {
            "host_organization": "UCAR/NCAR",
            "access_model": "open",
            "api_available": True,
            "authentication_required": True,
            "license_options": ["CC BY 4.0", "custom research license"],
            "metadata_schema": "ISO 19115",
            "identifier_system": "DOI",
            "sample_query": "https://rda.ucar.edu/api/v1/datasets/?format=json",
            "rate_limits": "100 requests/hour anonymous, 1000 authenticated",
            "download_methods": ["HTTP", "Globus", "OPeNDAP"],
            "data_domains": ["climate", "atmospheric-science"],
            "size_estimate": "5 PB",
        },
        "reproducibility": {
            "level": "documented",
            "tested_with": [
                {"tool": "curl", "version": "8.5.0"},
            ],
            "tested_on_os": "Ubuntu 22.04 LTS",
            "limitations": "Repository description; access tested manually.",
            "last_verified_at": "2025-03-15",
        },
        "status": "published",
        "visibility": "public",
    },
    {
        "slug": "netcdf-to-zarr-workflow",
        "content_type_slug": "workflow",
        "title": "NetCDF to Zarr Conversion Workflow",
        "body_md": (
            "## Problem\n\n"
            "NetCDF-4 files are optimized for POSIX filesystems and parallel I/O via "
            "MPI-IO, but they perform poorly on object stores (S3, GCS) because each "
            "variable access requires multiple HTTP range requests. "
            "[Zarr](https://zarr.dev/) stores each chunk as a separate object, making "
            "it ideal for cloud-native access.\n\n"
            "## Steps\n\n"
            "### 1. Open the source dataset\n\n"
            "```python\n"
            "import xarray as xr\n\n"
            "ds = xr.open_dataset(\n"
            "    'tas_day_CESM2_historical.nc',\n"
            "    chunks={'time': 365, 'lat': 90, 'lon': 180},\n"
            ")\n"
            "```\n\n"
            "### 2. Write to Zarr\n\n"
            "```python\n"
            "ds.to_zarr('tas_day_CESM2_historical.zarr', mode='w')\n"
            "```\n\n"
            "### 3. Verify the output\n\n"
            "```python\n"
            "ds_zarr = xr.open_zarr('tas_day_CESM2_historical.zarr')\n"
            "xr.testing.assert_identical(ds, ds_zarr)\n"
            "print('Conversion verified — datasets are identical.')\n"
            "```\n\n"
            "## Common Errors\n\n"
            "- **ValueError: wrong chunk size** — Ensure chunk dimensions align with "
            "the variable shape; use `ds.chunk()` to re-chunk before writing.\n"
            "- **PermissionError** — Check file permissions on the output directory."
        ),
        "extra_data": {
            "problem_statement": (
                "Convert NetCDF-4 climate data to Zarr for cloud-optimized access"
            ),
            "skill_level": "beginner",
            "estimated_minutes": 15,
            "inputs": [
                {"name": "input.nc", "format": "netcdf", "size_hint": "~100 MB"},
            ],
            "tools_required": ["xarray", "cf_xarray"],
            "steps_summary": [
                "open dataset", "inspect structure", "select variable", "export",
            ],
            "code_language": "Python",
            "expected_output_summary": (
                "xarray.DataArray with lat/lon/time dimensions"
            ),
            "common_errors": [
                "ValueError: wrong chunk size",
                "PermissionError: check file permissions",
            ],
            "tested_on": {
                "python": "3.12",
                "packages": {"xarray": "2024.10"},
            },
        },
        "reproducibility": {
            "level": "verified",
            "tested_with": [
                {"tool": "Python", "version": "3.12.1"},
                {"tool": "xarray", "version": "2024.10.0"},
            ],
            "tested_on_os": "Ubuntu 22.04 LTS",
            "input_example": "sample.nc — 1 MB, 10 variables, 3 dimensions",
            "expected_output_summary": "xarray.Dataset with 10 data variables",
            "checksum": "sha256:a3f2bc...",
            "limitations": (
                "Does not handle files larger than available RAM; use chunking."
            ),
            "last_verified_at": "2025-03-15",
            "verified_by": "admin",
        },
        "status": "published",
        "visibility": "public",
    },
    {
        "slug": "chunked-io-concept",
        "content_type_slug": "concept_guide",
        "title": "Chunked I/O for Large Scientific Datasets",
        "body_md": (
            "## What Is Chunked I/O?\n\n"
            "Chunked I/O is a strategy for reading and writing large datasets in "
            "fixed-size blocks (chunks) rather than loading the entire array into "
            "memory. This is the foundation of scalable scientific computing — without "
            "it, datasets that exceed available RAM cannot be processed at all.\n\n"
            "## How Chunks Work\n\n"
            "A chunk is a contiguous sub-array stored as a single unit on disk. When "
            "you access a variable, only the chunks overlapping your selection are read. "
            "For example, a 10 GB temperature field chunked by `(365, 90, 180)` "
            "can be sliced along the time axis without touching spatial data:\n\n"
            "```python\n"
            "import xarray as xr\n\n"
            "ds = xr.open_dataset('large_model_output.nc', chunks={'time': 365})\n"
            "january = ds['temperature'].sel(time='2024-01')\n"
            "# Only the chunks covering January are read from disk\n"
            "```\n\n"
            "## Key Terms\n\n"
            "- **Chunk** — A fixed-size sub-array stored and read as one unit\n"
            "- **Shard** — A group of chunks stored in a single file (Zarr v3)\n"
            "- **Stride** — The step size between elements when iterating over an array\n"
            "- **Cache** — In-memory buffer for recently accessed chunks"
        ),
        "extra_data": {
            "skill_level": "intermediate",
            "related_formats": ["hdf5", "netcdf", "zarr"],
            "related_tools": ["h5py", "xarray"],
            "key_terms": ["chunk", "shard", "cache", "stride"],
            "further_reading_dois": ["10.1000/xyz123"],
        },
        "reproducibility": {
            "level": "documented",
            "tested_with": [
                {"tool": "xarray", "version": "2024.10.0"},
            ],
            "tested_on_os": "Ubuntu 22.04 LTS",
            "limitations": "Conceptual guide; code snippets tested manually.",
            "last_verified_at": "2025-03-15",
        },
        "status": "published",
        "visibility": "public",
    },
]

RELATIONS = [
    {"from_slug": "xarray", "to_slug": "netcdf-4", "rel_type": "reads"},
    {"from_slug": "netcdf-to-zarr-workflow", "to_slug": "xarray", "rel_type": "uses"},
    {
        "from_slug": "netcdf-to-zarr-workflow",
        "to_slug": "netcdf-4",
        "rel_type": "input_format",
    },
    {
        "from_slug": "netcdf-to-zarr-workflow",
        "to_slug": "ncar-rda",
        "rel_type": "source_repository",
    },
    {
        "from_slug": "chunked-io-concept",
        "to_slug": "netcdf-to-zarr-workflow",
        "rel_type": "related_to",
    },
    {"from_slug": "netcdf-4", "to_slug": "xarray", "rel_type": "supported_by"},
]

SOURCES = [
    {
        "title": "NetCDF-4 Format Specification",
        "url": "https://www.unidata.ucar.edu/software/netcdf/docs/file_format_specifications.html",
        "source_type": "official_spec",
        "links": [
            {"item_slug": "netcdf-4", "link_role": "primary_spec"},
        ],
    },
    {
        "title": "xarray Documentation",
        "url": "https://docs.xarray.dev/en/stable/",
        "source_type": "official_docs",
        "links": [
            {"item_slug": "xarray", "link_role": "documentation"},
        ],
    },
    {
        "title": "NCAR Research Data Archive",
        "url": "https://rda.ucar.edu/",
        "source_type": "repository",
        "links": [
            {"item_slug": "ncar-rda", "link_role": "primary_spec"},
            {"item_slug": "netcdf-to-zarr-workflow", "link_role": "related"},
        ],
    },
    {
        "title": "Xarray: N-D labeled Arrays and Datasets in Python (Hoyer & Hamman 2017)",
        "url": "https://doi.org/10.5334/jors.148",
        "source_type": "paper",
        "identifier_type": "DOI",
        "identifier_value": "10.5334/jors.148",
        "links": [
            {"item_slug": "xarray", "link_role": "paper"},
        ],
    },
]

TAG_ASSIGNMENTS = {
    "netcdf-4": ["climate", "netcdf", "parallel-io"],
    "xarray": ["python", "netcdf", "format-conversion"],
    "ncar-rda": ["climate", "atmospheric-science"],
    "netcdf-to-zarr-workflow": [
        "python", "format-conversion", "cloud-storage", "intermediate",
    ],
    "chunked-io-concept": ["parallel-io", "performance-tuning", "intermediate"],
}


class Command(BaseCommand):
    help = "Seed the database with content types, tags, superuser, and sample content"

    def handle(self, *args, **options):
        # Step 1: Seed content types with extra_schema
        ct_created = 0
        for ct_data in CONTENT_TYPES:
            _, created = ContentTypeDef.objects.update_or_create(
                slug=ct_data["slug"],
                defaults={**ct_data, "extra_schema": EXTRA_SCHEMAS[ct_data["slug"]]},
            )
            if created:
                ct_created += 1

        self.stdout.write(
            f"Content types: {ct_created} created, "
            f"{len(CONTENT_TYPES) - ct_created} already existed"
        )

        # Step 2: Seed tags
        tag_created = 0
        for category, slugs in TAGS.items():
            for slug in slugs:
                name = slug.replace("-", " ").replace("_", " ").title()
                _, created = Tag.objects.update_or_create(
                    slug=slug,
                    defaults={
                        "name": name,
                        "category": category,
                    },
                )
                if created:
                    tag_created += 1

        total_tags = sum(len(v) for v in TAGS.values())
        self.stdout.write(
            f"Tags: {tag_created} created, "
            f"{total_tags - tag_created} already existed"
        )

        # Step 3: Ensure superuser exists
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            superuser = User.objects.create_superuser(
                "admin", "admin@localhost", "admin"
            )
            self.stdout.write(
                self.style.WARNING(
                    "Superuser created: admin / admin "
                    "— change in production"
                )
            )
        else:
            superuser = User.objects.filter(is_superuser=True).first()
            self.stdout.write("Superuser already exists")

        # Step 4: Seed content items
        items_cache = {}
        items_created = 0
        for item_data in SEED_ITEMS:
            data = {k: v for k, v in item_data.items() if k != "content_type_slug"}
            ct = ContentTypeDef.objects.get(slug=item_data["content_type_slug"])
            item, created = ContentItem.objects.update_or_create(
                slug=data.pop("slug"),
                defaults={**data, "content_type": ct, "created_by": superuser},
            )
            items_cache[item_data["slug"]] = item
            if created:
                items_created += 1

        self.stdout.write(
            f"Content items: {items_created} created, "
            f"{len(SEED_ITEMS) - items_created} already existed"
        )

        # Step 5: Seed tag assignments
        tag_assign_created = 0
        for item_slug, tag_slugs in TAG_ASSIGNMENTS.items():
            item = items_cache[item_slug]
            for tag_slug in tag_slugs:
                tag = Tag.objects.get(slug=tag_slug)
                _, created = ContentTag.objects.get_or_create(
                    content_item=item, tag=tag,
                )
                if created:
                    tag_assign_created += 1

        total_assigns = sum(len(v) for v in TAG_ASSIGNMENTS.values())
        self.stdout.write(
            f"Tag assignments: {tag_assign_created} created, "
            f"{total_assigns - tag_assign_created} already existed"
        )

        # Step 6: Seed relations
        rel_created = 0
        for rel in RELATIONS:
            from_item = items_cache[rel["from_slug"]]
            to_item = items_cache[rel["to_slug"]]
            _, created = ContentRelation.objects.get_or_create(
                from_item=from_item,
                to_item=to_item,
                rel_type=rel["rel_type"],
                defaults={"notes": rel.get("notes", "")},
            )
            if created:
                rel_created += 1

        self.stdout.write(
            f"Relations: {rel_created} created, "
            f"{len(RELATIONS) - rel_created} already existed"
        )

        # Step 7: Seed source references and links
        src_created = 0
        link_created = 0
        for src_data in SOURCES:
            links = src_data.pop("links", [])
            source, created = SourceReference.objects.update_or_create(
                title=src_data["title"],
                defaults={k: v for k, v in src_data.items() if k != "title"},
            )
            # Restore links for idempotency on re-run
            src_data["links"] = links
            if created:
                src_created += 1
            for link in links:
                item = items_cache[link["item_slug"]]
                _, lk_created = ContentSourceLink.objects.get_or_create(
                    content_item=item,
                    source_ref=source,
                    link_role=link["link_role"],
                )
                if lk_created:
                    link_created += 1

        self.stdout.write(
            f"Sources: {src_created} created, "
            f"{len(SOURCES) - src_created} already existed"
        )
        self.stdout.write(
            f"Source links: {link_created} created"
        )

        self.stdout.write(self.style.SUCCESS("Seeding complete."))
