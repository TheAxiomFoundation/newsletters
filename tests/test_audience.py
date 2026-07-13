"""Tests for audience targeting."""

import pytest

from newsletter_uploader.audience import AudienceType, get_segment_opts


class TestAudienceType:
    """Test AudienceType enum."""

    def test_audience_types_exist(self):
        """Test all audience types are defined."""
        assert AudienceType.UK
        assert AudienceType.US
        assert AudienceType.ALL

    def test_audience_type_values(self):
        """Test audience type string values."""
        assert AudienceType.UK.value == "uk"
        assert AudienceType.US.value == "us"
        assert AudienceType.ALL.value == "all"


class TestGetSegmentOpts:
    """Test get_segment_opts function."""

    def test_uk_segment(self):
        """Test UK audience segment options."""
        opts = get_segment_opts(AudienceType.UK)

        assert opts is not None
        assert opts["match"] == "all"
        assert len(opts["conditions"]) == 1

        condition = opts["conditions"][0]
        assert condition["condition_type"] == "SelectMerge"
        assert condition["field"] == "COUNTRY"
        assert condition["op"] == "is"
        assert condition["value"] == "United Kingdom"

    def test_us_segment(self):
        """Test US (non-UK) audience segment options."""
        opts = get_segment_opts(AudienceType.US)

        assert opts is not None
        assert opts["match"] == "all"
        assert len(opts["conditions"]) == 1

        condition = opts["conditions"][0]
        assert condition["condition_type"] == "SelectMerge"
        assert condition["field"] == "COUNTRY"
        assert condition["op"] == "not"
        assert condition["value"] == "United Kingdom"

    def test_all_segment(self):
        """Test ALL audience returns None (no filtering)."""
        opts = get_segment_opts(AudienceType.ALL)
        assert opts is None

    def test_from_string(self):
        """Test creating AudienceType from string."""
        assert AudienceType("uk") == AudienceType.UK
        assert AudienceType("us") == AudienceType.US
        assert AudienceType("all") == AudienceType.ALL

    def test_invalid_audience_type(self):
        """Test invalid audience type raises error."""
        with pytest.raises(ValueError):
            AudienceType("invalid")
