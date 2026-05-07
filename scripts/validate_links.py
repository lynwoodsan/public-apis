#!/usr/bin/env python3
"""Script to validate links in the README.md file.

This script checks all URLs found in the README.md to ensure they are
accessible and return valid HTTP responses. It reports broken or
unreachable links.
"""

import re
import sys
import time
import argparse
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from concurrent.futures import ThreadPoolExecutor, as_completed

# Regex pattern to extract URLs from markdown
URL_PATTERN = re.compile(r'https?://[^\s\)\]>"\']+')

# HTTP headers to mimic a browser request
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; link-checker/1.0)'
}

# Timeout in seconds for each request
REQUEST_TIMEOUT = 10

# Maximum number of retries for failed requests
MAX_RETRIES = 2

# Delay between retries in seconds
RETRY_DELAY = 2


def extract_urls(filepath: str) -> list[str]:
    """Extract all URLs from a given file.

    Args:
        filepath: Path to the file to extract URLs from.

    Returns:
        A list of unique URLs found in the file.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    urls = URL_PATTERN.findall(content)
    # Remove duplicates while preserving order
    seen = set()
    unique_urls = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
    return unique_urls


def check_url(url: str) -> tuple[str, int | None, str | None]:
    """Check if a URL is accessible.

    Args:
        url: The URL to check.

    Returns:
        A tuple of (url, status_code, error_message).
        status_code is None if the request failed entirely.
        error_message is None if the request succeeded.
    """
    for attempt in range(MAX_RETRIES + 1):
        try:
            req = Request(url, headers=HEADERS)
            with urlopen(req, timeout=REQUEST_TIMEOUT) as response:
                return (url, response.status, None)
        except HTTPError as e:
            # HTTP errors (4xx, 5xx) are still responses
            return (url, e.code, str(e.reason))
        except URLError as e:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue
            return (url, None, str(e.reason))
        except Exception as e:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue
            return (url, None, str(e))
    return (url, None, 'Max retries exceeded')


def validate_links(filepath: str, max_workers: int = 10) -> bool:
    """Validate all links in a file.

    Args:
        filepath: Path to the markdown file to validate.
        max_workers: Maximum number of concurrent workers for link checking.

    Returns:
        True if all links are valid, False otherwise.
    """
    print(f'Extracting URLs from {filepath}...')
    urls = extract_urls(filepath)
    print(f'Found {len(urls)} unique URLs. Checking...')

    broken_links = []
    checked = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(check_url, url): url for url in urls}
        for future in as_completed(future_to_url):
            url, status, error = future.result()
            checked += 1
            if error or (status and status >= 400):
                broken_links.append((url, status, error))
                print(f'  [FAIL] {url} -> Status: {status}, Error: {error}')
            else:
                print(f'  [OK]   {url} -> {status}')

    print(f'\nResults: {checked} checked, {len(broken_links)} broken.')

    if broken_links:
        print('\nBroken links:')
        for url, status, error in broken_links:
            print(f'  - {url} (status={status}, error={error})')
        return False

    return True


def main():
    """Main entry point for the link validation script."""
    parser = argparse.ArgumentParser(
        description='Validate links in a markdown file.'
    )
    parser.add_argument(
        'filepath',
        nargs='?',
        default='README.md',
        help='Path to the markdown file to validate (default: README.md)'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=10,
        help='Number of concurrent workers (default: 10)'
    )
    args = parser.parse_args()

    success = validate_links(args.filepath, max_workers=args.workers)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
