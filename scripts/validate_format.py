#!/usr/bin/env python3
"""Validate the format and structure of the README.md API list.

This script checks that the README.md file follows the expected format:
- Categories are properly formatted as headers
- Tables have the correct columns
- Entries follow the expected structure
- Alphabetical ordering within categories
"""

import re
import sys
from pathlib import Path

# Expected table header format
EXPECTED_HEADER = '| API | Description | Auth | HTTPS | CORS |'
EXPECTED_SEPARATOR = '|---|---|---|---|---|'

# Valid values for specific columns
# Note: added 'OAuth2' as I've seen it used in some entries alongside 'OAuth'
VALID_AUTH_VALUES = {'apiKey', 'OAuth', 'OAuth2', 'X-Mashape-Key', 'User-Agent', 'No', ''}
VALID_HTTPS_VALUES = {'Yes', 'No'}
VALID_CORS_VALUES = {'Yes', 'No', 'Unknown'}

# Regex patterns
CATEGORY_PATTERN = re.compile(r'^### (.+)$')
TABLE_ROW_PATTERN = re.compile(r'^\|(.+)\|$')
LINK_PATTERN = re.compile(r'^\[.+\]\(.+\)$')


def parse_readme(filepath: str) -> dict:
    """Parse the README.md file and extract categories with their entries.

    Args:
        filepath: Path to the README.md file.

    Returns:
        A dict mapping category names to lists of row strings.
    """
    categories = {}
    current_category = None
    in_table = False

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.rstrip('\n')

        category_match = CATEGORY_PATTERN.match(line)
        if category_match:
            current_category = category_match.group(1)
            categories[current_category] = []
            in_table = False
            continue

        if current_category is None:
            continue

        if EXPECTED_HEADER in line:
            in_table = True
            continue

        if in_table and line.startswith('|---|'):
            continue

        if in_table and TABLE_ROW_PATTERN.match(line):
            categories[current_category].append(line)
        elif in_table and line.strip() == '':
            in_table = False

    return categories


def validate_row_format(row: str, category: str, row_index: int) -> list:
    """Validate a single table row for correct format.

    Args:
        row: The raw table row string.
        category: The category this row belongs to.
        row_index: The index of this row within its category.

    Returns:
        A list of error message strings (empty if valid).
    """
    errors = []
    prefix = f"[{category}] Row {row_index + 1}"

    # Strip leading/trailing pipes and split
    cells = [cell.strip() for cell in row.strip('|').split('|')]

    if len(cells) != 5:
        errors.append(f"{prefix}: Expected 5 columns, got {len(cells)}")
        return errors

    api_name, description, auth, https, cors = cells

    # Validate API name (should be a markdown link)
    if not LINK_PATTERN.match(api_name):
        errors.append(f"{prefix}: API name should be a markdown link, got: '{api_name}'")

    # Validate description is not empty
    if not description.strip():
        errors.append(f"{prefix}: Description should not be empty")

    # Validate auth value
    if auth not in VALID_AUTH_VALUES:
        errors.append(f"{prefix}: Invalid Auth value '{auth}', expected one of {VALID_AUTH_VALUES}")

    # Validate HTTPS value
    if https not in VALID_HTTPS_VALUES:
        errors.append(f"{prefix}: Invalid HTTPS value '{https}', expected one of {VALID_HTTPS_VALUES}")

    # Validate CORS value
    if cors not in VALID_CORS_VALUES:
        errors.append(f"{prefix}: Invalid CORS value '{cors}', expected one of {VALID_CORS_VALUES}")

    return errors
