#!/usr/bin/env python3
"""Validate API entries in the README.md file.

This script checks that all entries in the public-apis list follow
the required format and contain valid data.
"""

import re
import sys
from pathlib import Path

# Expected table header format
TABLE_HEADER = '| API | Description | Auth | HTTPS | CORS |'
TABLE_SEPARATOR = '|---|---|---|---|---|'

# Valid values for specific columns
VALID_AUTH = {'apiKey', 'OAuth', 'X-Mashape-Key', 'User-Agent', 'No', ''}
VALID_HTTPS = {'Yes', 'No'}
VALID_CORS = {'Yes', 'No', 'Unknown'}

# Regex pattern for a valid table row
ROW_PATTERN = re.compile(
    r'^\|\s*\[.+\]\(.+\)\s*'
    r'\|\s*.+\s*'
    r'\|\s*(apiKey|OAuth|X-Mashape-Key|User-Agent|No|`[^`]+`)\s*'
    r'\|\s*(Yes|No)\s*'
    r'\|\s*(Yes|No|Unknown)\s*\|$'
)

# Maximum allowed length for a description — helps keep entries concise
# Bumped from 100 to 120 since some legitimate APIs have longer descriptions
MAX_DESCRIPTION_LENGTH = 120


def parse_table_row(row: str) -> list[str] | None:
    """Parse a markdown table row into its columns.

    Args:
        row: A markdown table row string.

    Returns:
        A list of column values, or None if the row is not a valid table row.
    """
    row = row.strip()
    if not row.startswith('|') or not row.endswith('|'):
        return None
    columns = [col.strip() for col in row[1:-1].split('|')]
    return columns


def validate_entry(row: str, line_num: int) -> list[str]:
    """Validate a single API entry row.

    Args:
        row: The markdown table row to validate.
        line_num: The line number in the file (for error reporting).

    Returns:
        A list of error messages. Empty list means the entry is valid.
    """
    errors = []
    columns = parse_table_row(row)

    if columns is None or len(columns) != 5:
        errors.append(f'Line {line_num}: Invalid row format — expected 5 columns, got {len(columns) if columns else 0}')
        return errors

    api_name, description, auth, https, cors = columns

    # Validate API name (must be a markdown link)
    if not re.match(r'^\[.+\]\(https?://.+\)$', api_name):
        errors.append(f'Line {line_num}: API name must be a valid markdown link: "{api_name}"')

    # Validate description is not empty
    if not description:
        errors.append(f'Line {line_num}: Description must not be empty')

    # Validate description does not end with a period
    if description.endswith('.'):
        errors.append(f'Line {line_num}: Description must not end with a period: "{description}"')

    # Validate description length — long descriptions clutter the table
    if len(description) > MAX_DESCRIPTION_LENGTH:
        errors.append(f'Line {line_num}: Description too long ({len(description)} chars, max {MAX_DESCRIPTION_LENGTH}): "{description}"')

    # Validate auth value
    if auth not in VALID_AUTH and not re.match(r'^`[^`]+`$', auth):
        errors.append(f'Line {line_num}: Invalid Auth value "{auth}". Must be one of {VALID_AUTH}')

    # Validate HTTPS value
    if https not in VALID_HTTPS:
        err