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
VALID_AUTH_VALUES = {'apiKey', 'OAuth', 'X-Mashape-Key', 'User-Agent', 'No', ''}
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

    # Validate Auth column
    if auth not in VALID_AUTH_VALUES:
        errors.append(f"{prefix}: Invalid Auth value '{auth}', expected one of {VALID_AUTH_VALUES}")

    # Validate HTTPS column
    if https not in VALID_HTTPS_VALUES:
        errors.append(f"{prefix}: Invalid HTTPS value '{https}', expected one of {VALID_HTTPS_VALUES}")

    # Validate CORS column
    if cors not in VALID_CORS_VALUES:
        errors.append(f"{prefix}: Invalid CORS value '{cors}', expected one of {VALID_CORS_VALUES}")

    return errors


def validate_alphabetical_order(entries: list, category: str) -> list:
    """Check that entries within a category are sorted alphabetically by API name.

    Args:
        entries: List of table row strings.
        category: The category name for error messages.

    Returns:
        A list of error message strings (empty if valid).
    """
    errors = []
    api_names = []

    for row in entries:
        cells = [cell.strip() for cell in row.strip('|').split('|')]
        if cells:
            # Extract just the display name from the markdown link
            match = re.match(r'^\[(.+?)\]', cells[0])
            if match:
                api_names.append(match.group(1).lower())

    sorted_names = sorted(api_names)
    if api_names != sorted_names:
        errors.append(f"[{category}]: Entries are not in alphabetical order")

    return errors


def validate_format(filepath: str) -> bool:
    """Run all format validations on the README.md file.

    Args:
        filepath: Path to the README.md file.

    Returns:
        True if all validations pass, False otherwise.
    """
    categories = parse_readme(filepath)
    all_errors = []

    for category, entries in categories.items():
        for i, row in enumerate(entries):
            errors = validate_row_format(row, category, i)
            all_errors.extend(errors)

        order_errors = validate_alphabetical_order(entries, category)
        all_errors.extend(order_errors)

    if all_errors:
        print(f"Found {len(all_errors)} format error(s):\n")
        for error in all_errors:
            print(f"  - {error}")
        return False

    print(f"All format checks passed! Validated {len(categories)} categories.")
    return True


def main():
    """Entry point for the format validation script."""
    readme_path = Path(__file__).parent.parent / 'README.md'

    if not readme_path.exists():
        print(f"Error: README.md not found at {readme_path}")
        sys.exit(1)

    success = validate_format(str(readme_path))
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
