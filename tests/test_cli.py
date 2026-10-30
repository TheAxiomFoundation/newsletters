"""Tests for CLI interface."""

import pytest
from click.testing import CliRunner

from newsletter_uploader.cli import main


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


@pytest.fixture
def html_file(tmp_path):
    """Create a test HTML file."""
    html_path = tmp_path / "test.html"
    html_path.write_text("<html><body>Test</body></html>")
    return html_path


class TestCLI:
    """Test CLI interface."""

    def test_cli_requires_html_file(self, runner):
        """Test CLI requires HTML file argument."""
        result = runner.invoke(main, [])
        assert result.exit_code != 0
        assert (
            "Missing argument" in result.output or "required" in result.output.lower()
        )

    def test_cli_requires_audience(self, runner, html_file):
        """Test CLI requires --audience option."""
        result = runner.invoke(
            main,
            [
                str(html_file),
                "--subject",
                "Test",
                "--preview",
                "Preview",
                "--api-key",
                "test-key-us5",
            ],
        )
        assert result.exit_code != 0
        assert "audience" in result.output.lower()

    def test_cli_requires_subject(self, runner, html_file):
        """Test CLI requires --subject option."""
        result = runner.invoke(
            main,
            [
                str(html_file),
                "--audience",
                "uk",
                "--preview",
                "Preview",
                "--api-key",
                "test-key-us5",
            ],
        )
        assert result.exit_code != 0
        assert "subject" in result.output.lower()

    def test_cli_requires_preview(self, runner, html_file):
        """Test CLI requires --preview option."""
        result = runner.invoke(
            main,
            [
                str(html_file),
                "--audience",
                "uk",
                "--subject",
                "Test",
                "--api-key",
                "test-key-us5",
            ],
        )
        assert result.exit_code != 0
        assert "preview" in result.output.lower()

    def test_cli_requires_api_key(self, runner, html_file):
        """Test CLI requires API key."""
        result = runner.invoke(
            main,
            [
                str(html_file),
                "--audience",
                "uk",
                "--subject",
                "Test",
                "--preview",
                "Preview",
            ],
        )
        assert result.exit_code == 1
        assert "MAILCHIMP_API_KEY not found" in result.output

    def test_cli_requires_list_id(self, runner, html_file):
        """Test CLI requires list ID."""
        result = runner.invoke(
            main,
            [
                str(html_file),
                "--audience",
                "uk",
                "--subject",
                "Test",
                "--preview",
                "Preview",
                "--api-key",
                "test-key-us5",
            ],
        )
        assert result.exit_code == 1
        assert "MAILCHIMP_LIST_ID not found" in result.output

    def test_cli_accepts_valid_audiences(self, runner, html_file, mocker):
        """Test CLI accepts valid audience values."""
        # Mock the MailchimpClient and uploader
        mocker.patch("newsletter_uploader.cli.MailchimpClient")
        mock_uploader = mocker.patch(
            "newsletter_uploader.cli.NewsletterUploader"
        ).return_value
        mock_uploader.upload.return_value = {
            "campaign_id": "test123",
            "web_id": 12345,
        }

        for audience in ["uk", "us", "all"]:
            result = runner.invoke(
                main,
                [
                    str(html_file),
                    "--audience",
                    audience,
                    "--subject",
                    "Test",
                    "--preview",
                    "Preview",
                    "--api-key",
                    "test-key-us5",
                    "--list-id",
                    "test-list-id",
                ],
            )
            assert result.exit_code == 0

    def test_cli_rejects_invalid_audience(self, runner, html_file):
        """Test CLI rejects invalid audience values."""
        result = runner.invoke(
            main,
            [
                str(html_file),
                "--audience",
                "invalid",
                "--subject",
                "Test",
                "--preview",
                "Preview",
                "--api-key",
                "test-key-us5",
            ],
        )
        assert result.exit_code != 0
        assert "invalid" in result.output.lower() or "choice" in result.output.lower()

    def test_cli_success_output(self, runner, html_file, mocker):
        """Test CLI success output formatting."""
        mocker.patch("newsletter_uploader.cli.MailchimpClient")
        mock_uploader = mocker.patch(
            "newsletter_uploader.cli.NewsletterUploader"
        ).return_value
        mock_uploader.upload.return_value = {
            "campaign_id": "abc123",
            "web_id": 99999,
        }

        result = runner.invoke(
            main,
            [
                str(html_file),
                "--audience",
                "uk",
                "--subject",
                "Test Subject",
                "--preview",
                "Test Preview",
                "--api-key",
                "test-key-us5",
                "--list-id",
                "test-list-id",
            ],
        )

        assert result.exit_code == 0
        assert "✅ DRAFT CAMPAIGN CREATED SUCCESSFULLY" in result.output
        assert "abc123" in result.output
        assert "99999" in result.output
        assert "Test Subject" in result.output
        assert "Edit in Mailchimp" in result.output

    def test_cli_handles_file_not_found(self, runner, mocker):
        """Test CLI handles file not found error."""
        result = runner.invoke(
            main,
            [
                "nonexistent.html",
                "--audience",
                "uk",
                "--subject",
                "Test",
                "--preview",
                "Preview",
                "--api-key",
                "test-key-us5",
            ],
        )
        # File should not exist, so Click should error before we even try to upload
        assert result.exit_code != 0

    @pytest.mark.parametrize("campaign_id", [None, "campaign123"])
    def test_cli_refuses_hosting_links_before_mailchimp(
        self, runner, tmp_path, mocker, campaign_id
    ):
        """The CLI refuses hosting links for new campaigns and draft updates."""
        html_path = tmp_path / "2026-11-03-global.html"
        html_path.write_text(
            '<html><body><a href="https://axiom-preview.vercel.app/">'
            "Dashboard</a></body></html>"
        )
        client = mocker.patch("newsletter_uploader.cli.MailchimpClient").return_value
        args = [
            str(html_path),
            "--subject",
            "Test",
            "--preview",
            "Preview",
            "--api-key",
            "test-key-us5",
            "--list-id",
            "test-list-id",
        ]
        if campaign_id:
            args.extend(["--campaign-id", campaign_id])
        else:
            args.extend(["--audience", "all"])

        result = runner.invoke(main, args)

        assert result.exit_code == 1
        assert "axiom-preview.vercel.app" in result.output
        assert "axiom.org" in result.output
        assert client.mock_calls == []

    def test_cli_refuses_a_hosting_link_in_the_subject(self, runner, tmp_path, mocker):
        """A hosting address in --subject stops the CLI before Mailchimp."""
        html_path = tmp_path / "2026-11-03-global.html"
        html_path.write_text("<html><body>Clean</body></html>")
        client = mocker.patch("newsletter_uploader.cli.MailchimpClient").return_value

        result = runner.invoke(
            main,
            [
                str(html_path),
                "--audience",
                "all",
                "--subject",
                "New: axiom-preview.vercel.app",
                "--preview",
                "Preview",
                "--api-key",
                "test-key-us5",
                "--list-id",
                "test-list-id",
            ],
        )

        assert result.exit_code == 1
        assert "subject line" in result.output
        assert client.mock_calls == []
