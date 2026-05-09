#!/usr/bin/env python3
"""Validate the entire public-apis package by running all validation scripts.

This script serves as the main entry point for validating the README.md,
checking entry format, validating entry content, and optionally checking URLs.
"""

import argparse
import sys
import os

# Ensure scripts directory is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from validate_format import parse_readme, validate_row_format
from validate_entries import validate_entries


README_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'README.md')


def run_format_validation(readme_path: str) -> bool:
    """Run format validation on the README file.

    Args:
        readme_path: Path to the README.md file.

    Returns:
        True if all format checks pass, False otherwise.
    """
    print('\n=== Running Format Validation ===')
    errors = []

    try:
        categories = parse_readme(readme_path)
    except Exception as e:
        print(f'ERROR: Failed to parse README: {e}')
        return False

    for category, rows in categories.items():
        for row in rows:
            row_errors = validate_row_format(row)
            if row_errors:
                for err in row_errors:
                    errors.append(f'[{category}] {err}')

    if errors:
        print(f'Found {len(errors)} format error(s):')
        for err in errors:
            print(f'  - {err}')
        return False

    print(f'Format validation passed. Checked {sum(len(r) for r in categories.values())} entries.')
    return True


def run_entry_validation(readme_path: str) -> bool:
    """Run entry content validation on the README file.

    Args:
        readme_path: Path to the README.md file.

    Returns:
        True if all entry checks pass, False otherwise.
    """
    print('\n=== Running Entry Validation ===')

    try:
        success, errors = validate_entries(readme_path)
    except Exception as e:
        print(f'ERROR: Failed to validate entries: {e}')
        return False

    if not success:
        print(f'Found {len(errors)} entry error(s):')
        for err in errors:
            print(f'  - {err}')
        return False

    print('Entry validation passed.')
    return True


def run_link_validation(readme_path: str) -> bool:
    """Run URL/link validation on the README file.

    Args:
        readme_path: Path to the README.md file.

    Returns:
        True if all link checks pass, False otherwise.
    """
    print('\n=== Running Link Validation ===')

    try:
        from validate_links import validate_links
        success = validate_links(readme_path)
    except Exception as e:
        print(f'ERROR: Failed to validate links: {e}')
        return False

    if not success:
        print('Link validation failed.')
        return False

    print('Link validation passed.')
    return True


def main() -> None:
    """Main entry point for the validation package."""
    parser = argparse.ArgumentParser(
        description='Validate the public-apis README.md file.'
    )
    parser.add_argument(
        '--readme',
        default=README_PATH,
        help='Path to the README.md file (default: project root README.md)'
    )
    parser.add_argument(
        '--skip-links',
        action='store_true',
        help='Skip URL/link validation (useful for faster local checks)'
    )
    parser.add_argument(
        '--links-only',
        action='store_true',
        help='Run only URL/link validation'
    )
    args = parser.parse_args()

    if not os.path.isfile(args.readme):
        print(f'ERROR: README file not found at: {args.readme}')
        sys.exit(1)

    results = []

    if args.links_only:
        results.append(run_link_validation(args.readme))
    else:
        results.append(run_format_validation(args.readme))
        results.append(run_entry_validation(args.readme))
        if not args.skip_links:
            results.append(run_link_validation(args.readme))

    print('\n=== Validation Summary ===')
    if all(results):
        print('All validations passed!')
        sys.exit(0)
    else:
        print('One or more validations failed.')
        sys.exit(1)


if __name__ == '__main__':
    main()
