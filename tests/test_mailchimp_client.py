"""Tests for Mailchimp client."""

import pytest
import responses

from newsletter_uploader.mailchimp_client import MailchimpClient


@pytest.fixture
def client():
    """Create a Mailchimp client for testing."""
    return MailchimpClient(api_key="test-key-us5", list_id="test-list-id")


class TestMailchimpClient:
    """Test MailchimpClient class."""

    def test_client_initialization(self, client):
        """Test client initializes with correct values."""
        assert client.api_key == "test-key-us5"
        assert client.list_id == "test-list-id"
        assert client.base_url == "https://us5.api.mailchimp.com/3.0"

    def test_client_extracts_datacenter_from_key(self):
        """Test datacenter extraction from API key."""
        client = MailchimpClient(api_key="test-key-us10", list_id="list-id")
        assert client.base_url == "https://us10.api.mailchimp.com/3.0"

    @responses.activate
    def test_create_campaign_success(self, client):
        """Test successful campaign creation."""
        responses.post(
            "https://us5.api.mailchimp.com/3.0/campaigns",
            json={
                "id": "campaign123",
                "web_id": 12345,
                "recipients": {"recipient_count": 100},
            },
            status=200,
        )

        campaign = client.create_campaign(
            subject="Test Subject",
            preview_text="Test Preview",
            title="Test Campaign",
            segment_opts=None,
        )

        assert campaign["id"] == "campaign123"
        assert campaign["web_id"] == 12345
        assert len(responses.calls) == 1

        # Verify request payload
        request_body = responses.calls[0].request.body
        assert b"Test Subject" in request_body
        assert b"Test Preview" in request_body

    @responses.activate
    def test_create_campaign_with_segment(self, client):
        """Test campaign creation with audience segment."""
        responses.post(
            "https://us5.api.mailchimp.com/3.0/campaigns",
            json={"id": "campaign123", "web_id": 12345},
            status=200,
        )

        segment_opts = {
            "match": "all",
            "conditions": [{"field": "COUNTRY", "op": "is", "value": "United Kingdom"}],
        }

        campaign = client.create_campaign(
            subject="UK Test",
            preview_text="Preview",
            title="UK Campaign",
            segment_opts=segment_opts,
        )

        assert campaign["id"] == "campaign123"
        # Verify segment was included in request
        request_body = responses.calls[0].request.body
        assert b"segment_opts" in request_body

    @responses.activate
    def test_upload_content_success(self, client):
        """Test successful HTML content upload."""
        responses.put(
            "https://us5.api.mailchimp.com/3.0/campaigns/campaign123/content",
            json={"html": "<html>Test</html>"},
            status=200,
        )

        client.upload_content("campaign123", "<html>Test</html>")

        assert len(responses.calls) == 1
        request_body = responses.calls[0].request.body
        assert b"<html>Test</html>" in request_body

    @responses.activate
    def test_upload_content_failure(self, client):
        """Test content upload handles errors."""
        responses.put(
            "https://us5.api.mailchimp.com/3.0/campaigns/campaign123/content",
            json={"error": "Invalid campaign"},
            status=404,
        )

        with pytest.raises(Exception, match="Error uploading content"):
            client.upload_content("campaign123", "<html>Test</html>")

    @responses.activate
    def test_create_campaign_failure(self, client):
        """Test campaign creation handles errors."""
        responses.post(
            "https://us5.api.mailchimp.com/3.0/campaigns",
            json={"error": "Invalid list ID"},
            status=400,
        )

        with pytest.raises(Exception, match="Error creating campaign"):
            client.create_campaign(
                subject="Test",
                preview_text="Preview",
                title="Campaign",
                segment_opts=None,
            )
