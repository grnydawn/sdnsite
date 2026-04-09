"""Management command to seed the 5 content types and initial tag taxonomy."""

from django.core.management.base import BaseCommand

from apps.content.models import ContentTypeDef
from apps.taxonomy.models import Tag


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


class Command(BaseCommand):
    help = "Seed the database with content types and initial tag taxonomy"

    def handle(self, *args, **options):
        # Seed content types
        ct_created = 0
        for ct_data in CONTENT_TYPES:
            _, created = ContentTypeDef.objects.update_or_create(
                slug=ct_data["slug"],
                defaults=ct_data,
            )
            if created:
                ct_created += 1

        self.stdout.write(
            f"Content types: {ct_created} created, "
            f"{len(CONTENT_TYPES) - ct_created} already existed"
        )

        # Seed tags
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

        self.stdout.write(self.style.SUCCESS("Seeding complete."))
