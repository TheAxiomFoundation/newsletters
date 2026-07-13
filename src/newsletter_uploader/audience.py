"""Audience targeting configuration for Mailchimp campaigns."""

from enum import Enum
from typing import Dict, Optional


class AudienceType(Enum):
    """Supported audience types for newsletter targeting."""

    UK = "uk"
    US = "us"
    ALL = "all"


def get_segment_opts(audience: AudienceType) -> Optional[Dict]:
    """
    Get Mailchimp segment options for the specified audience.

    Args:
        audience: The target audience type

    Returns:
        Segment options dict for Mailchimp API, or None for ALL audience

    Notes:
        - UK: Only subscribers with COUNTRY = "United Kingdom"
        - US: All subscribers where COUNTRY ≠ "United Kingdom"
          (includes US and missing country)
        - ALL: No filtering (returns None)
    """
    if audience == AudienceType.UK:
        return {
            "match": "all",
            "conditions": [
                {
                    "condition_type": "SelectMerge",
                    "field": "COUNTRY",
                    "op": "is",
                    "value": "United Kingdom",
                }
            ],
        }
    elif audience == AudienceType.US:
        return {
            "match": "all",
            "conditions": [
                {
                    "condition_type": "SelectMerge",
                    "field": "COUNTRY",
                    "op": "not",
                    "value": "United Kingdom",
                }
            ],
        }
    else:  # AudienceType.ALL
        return None
