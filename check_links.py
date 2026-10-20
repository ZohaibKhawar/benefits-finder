"""Check that every official link in the data files still opens, and flag stale benefits.

Run: python check_links.py        (exit code 1 if anything is broken)
"""

import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date

from finder.data import PROVINCE_FILES, load

STALE_AFTER_DAYS = 180
BROWSER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# Sites that refuse every script; check these by hand in a browser.
BLOCKS_SCRIPTS = ("ramq.gouv.qc.ca", "yukon.ca", "gov.nu.ca")


def fetch(url: str, headers: dict) -> str:
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return str(response.status)
    except urllib.error.HTTPError as error:
        return str(error.code)
    except Exception as error:  # timeouts, DNS, SSL
        return type(error).__name__


def curl_status(url: str) -> str:
    """Some provincial sites drop Python's requests but answer curl."""
    if not shutil.which("curl"):
        return "no-curl"
    result = subprocess.run(["curl", "-s", "-o", os.devnull, "-w", "%{http_code}", "-L", "--max-time", "20", url],
                            capture_output=True, text=True)
    return result.stdout.strip() or "curl-failed"


def status_of(url: str) -> str:
    # Python's default User-Agent first: canada.ca stalls fake browser ones. Some smaller
    # sites refuse Python, so those get a retry as a browser, then with curl.
    code = fetch(url, {})
    if code == "403":
        code = fetch(url, BROWSER)
    if code != "200":
        code = curl_status(url)
    if code != "200" and any(host in url for host in BLOCKS_SCRIPTS):
        return "blocked"
    return code


def main() -> int:
    benefits, links = {}, {}
    for province in PROVINCE_FILES:
        found, province_links = load(province)
        benefits.update(found)
        links.update({k: v for k, v in province_links.items() if k != "plan"})
    urls = {}
    for benefit in benefits.values():
        urls.setdefault(benefit["url"], []).append(benefit["id"])
        if "extra_url" in benefit:
            urls.setdefault(benefit["extra_url"], []).append(benefit["id"] + " (extra)")
    for name, url in links.items():
        if name != "plan":
            urls.setdefault(url, []).append(f"link:{name}")

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = dict(zip(urls, pool.map(status_of, urls)))

    broken = 0
    for url, code in sorted(results.items(), key=lambda pair: pair[1]):
        ok = code in ("200", "blocked")
        broken += not ok
        label = "ok " if code == "200" else "?? " if code == "blocked" else "BAD"
        print(f"{label} {code:>4}  {', '.join(urls[url])}  {url}")

    stale = [b["id"] for b in benefits.values() if (date.today() - b["last_checked"]).days > STALE_AFTER_DAYS]
    if stale:
        print(f"\nNot checked in {STALE_AFTER_DAYS}+ days: {', '.join(stale)}")
    print(f"\n{len(results) - broken} of {len(results)} links ok")
    return 1 if broken or stale else 0


if __name__ == "__main__":
    sys.exit(main())
