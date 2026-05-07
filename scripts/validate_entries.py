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

    # Validate auth value
    if auth not in VALID_AUTH and not re.match(r'^`[^`]+`$', auth):
        errors.append(f'Line {line_num}: Invalid Auth value "{auth}". Must be one of {VALID_AUTH}')

    # Validate HTTPS value
    if https not in VALID_HTTPS:
        errors.append(f'Line {line_num}: Invalid HTTPS value "{https}". Must be one of {VALID_HTTPS}')

    # Validate CORS value
    if cors not in VALID_CORS:
        errors.append(f'Line {line_num}: Invalid CORS value "{cors}". Must be one of {VALID_CORS}')

    return errors


def validate_entries(readme_path: str = 'README.md') -> bool:
    """Validate all API entries in the README file.

    Args:
        readme_path: Path to the README.md file.

    Returns:
        True if all entries are valid, False otherwise.
    """
    path = Path(readme_path)
    if not path.exists():
        print(f'Error: File not found: {readme_path}', file=sys.stderr)
        return False

    content = path.read_text(encoding='utf-8')
    lines = content.splitlines()

    all_errors = []
    in_table = False
    entry_count = 0

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Detect start of a table
        if stripped == TABLE_HEADER:
            in_table = True
            continue

        # Skip separator line
        if in_table and stripped == TABLE_SEPARATOR:
            continue

        # Process table rows
        if in_table and stripped.startswith('|') and stripped.endswith('|'):
            errors = validate_entry(stripped, line_num)
            all_errors.extend(errors)
            entry_count += 1
        elif in_table and stripped == '':
            in_table = False  # blank line ends the table

    if all_errors:
        print(f'Found {len(all_errors)} validation error(s):\n')
        for error in all_errors:
            print(f'  {error}')
        return False

    print(f'All {entry_count} entries are valid.')
    return True


def main() -> None:
    """Entry point for the validate_entries script."""
    readme = sys.argv[1] if len(sys.argv) > 1 else 'README.md'
    success = validate_entries(readme)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
