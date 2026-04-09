"""Tests for ContentItemAdmin JSONB validation (ADMIN-04).

Validates that extra_data is checked against ContentTypeDef.extra_schema
using jsonschema in the admin form's clean() method.
"""
import pytest

pytestmark = pytest.mark.django_db


class TestContentItemAdminJsonbValidation:
    """Test jsonschema validation in ContentItemAdminForm.clean()."""

    def test_valid_extra_data_passes_schema_validation(self):
        """extra_data matching the content type's extra_schema saves without error."""
        # TODO: Create ContentTypeDef with extra_schema, create ContentItem
        # with matching extra_data, submit via admin form, assert no ValidationError
        pytest.skip("Stub -- implement after ContentItemAdminForm is created")

    def test_invalid_extra_data_raises_validation_error(self):
        """extra_data violating the content type's extra_schema raises ValidationError."""
        # TODO: Create ContentTypeDef with extra_schema requiring {"url": string},
        # submit extra_data={"url": 123}, assert ValidationError on extra_data field
        pytest.skip("Stub -- implement after ContentItemAdminForm is created")

    def test_empty_extra_data_skips_validation(self):
        """Empty extra_data ({}) does not trigger schema validation."""
        # TODO: Create ContentTypeDef with extra_schema, submit extra_data={},
        # assert no ValidationError (empty dict is valid -- no required fields violated)
        pytest.skip("Stub -- implement after ContentItemAdminForm is created")

    def test_null_extra_schema_skips_validation(self):
        """ContentTypeDef with null extra_schema skips validation entirely."""
        # TODO: Create ContentTypeDef with extra_schema=None, submit any extra_data,
        # assert no ValidationError
        pytest.skip("Stub -- implement after ContentItemAdminForm is created")
