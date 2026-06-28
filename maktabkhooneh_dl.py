#!/usr/bin/env python3

# Standard library imports
import argparse
import getpass
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

# Third-party imports
from playwright.sync_api import sync_playwright

# -------------------- Selectors --------------------
CHAPTER_SELECTOR = "div[id^='course-chapter-']"
CHAPTER_TITLE_SELECTOR = "div[title^='فصل'] span.text-xl"
LESSON_SELECTOR = "a.group[href*='/ویدیو-']"
LESSON_TITLE_SELECTOR = "div.BaseChapterContentUnitTitle > span[title]"
DOWNLOAD_SELECTOR = ".unit-content--download a[download]"
LOGIN_BUTTON_SELECTOR = "button#login.button[type='button']"
MAKTABKHOONEH_BASE = "https://maktabkhooneh.org"
MAKTABKHOONEH_COURSE_PREFIX = f"{MAKTABKHOONEH_BASE}/course/"
# -------------------- End of Selectors --------------------


def slugify(txt: str) -> str:
    txt = re.sub(r"[^\w\s\-\.]", "", txt, flags=re.UNICODE)
    txt = re.sub(r"\s+", " ", txt, flags=re.UNICODE).strip()
    txt = txt.replace("/", "-")
    return txt


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def validate_url(url: str) -> str:
    """Validate that the URL is a maktabkhooneh.org course URL."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise argparse.ArgumentTypeError(f"Invalid URL scheme: '{parsed.scheme}'. Must be http or https.")
    if "maktabkhooneh.org" not in parsed.netloc:
        raise argparse.ArgumentTypeError(f"URL must be from maktabkhooneh.org, got: '{parsed.netloc}'")
    if "/course/" not in parsed.path:
        raise argparse.ArgumentTypeError("URL must point to a course page (must contain '/course/').")
    return url


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Batch download Maktabkhooneh course videos using Playwright.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python maktabkhooneh_dl.py --url https://maktabkhooneh.org/course/آموزش-پایتون-mk123/
  python maktabkhooneh_dl.py --url https://maktabkhooneh.org/course/... --output ./downloads

Credentials (in order of priority):
  1. --username / --password CLI flags
  2. MK_USERNAME / MK_PASSWORD environment variables
  3. Interactive prompt (password via getpass — hidden input)
        """,
    )
    parser.add_argument(
        "--url",
        dest="course_url",
        type=validate_url,
        default=None,
        help="Full URL of the Maktabkhooneh course page.",
    )
    parser.add_argument(
        "-u", "--username",
        dest="username",
        default=None,
        help="Maktabkhooneh account email or phone. Can also be set via MK_USERNAME env var.",
    )
    parser.add_argument(
        "-p", "--password",
        dest="password",
        default=None,
        help=(
            "Maktabkhooneh password. Prefer MK_PASSWORD env var or interactive prompt "
            "over this flag to avoid leaking credentials in shell history."
        ),
    )
    parser.add_argument(
        "--output",
        dest="output_dir",
        type=Path,
        default=Path("MK_Downloads"),
        help="Directory to save downloaded videos (default: MK_Downloads).",
    )
    parser.add_argument(
        "--profile",
        dest="user_data_dir",
        type=Path,
        default=Path("./mk_profile"),
        help="Path for browser profile storage (default: ./mk_profile).",
    )
    parser.add_argument(
        "--no-skip",
        dest="skip_if_exists",
        action="store_false",
        default=True,
        help="Re-download files even if they already exist (default: skip existing).",
    )
    return parser.parse_args()


def resolve_credentials(args: argparse.Namespace) -> tuple[str | None, str | None]:
    """Resolve username and password from CLI args → env vars → interactive prompt."""
    username = args.username or os.environ.get("MK_USERNAME")
    password = args.password or os.environ.get("MK_PASSWORD")

    if not username:
        username = input("Maktabkhooneh username (email/phone): ").strip() or None

    if not password:
        password = getpass.getpass("Maktabkhooneh password (hidden): ") or None

    return username, password


def main() -> None:
    args = parse_args()

    course_url = args.course_url
    if not course_url:
        raw = input("Please enter the course URL: ").strip()
        try:
            course_url = validate_url(raw)
        except argparse.ArgumentTypeError as e:
            print(f"[ERROR] {e}", file=sys.stderr)
            sys.exit(1)

    username, password = resolve_credentials(args)

    output_dir: Path = args.output_dir
    user_data_dir: Path = args.user_data_dir
    skip_if_exists: bool = args.skip_if_exists

    ensure_dir(output_dir)
    ensure_dir(user_data_dir)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            headless=False,
            viewport={"width": 1920, "height": 1080},
        )
        page = browser.new_page()

        page.goto(course_url, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        if page.query_selector(LOGIN_BUTTON_SELECTOR):
            if username and password:
                print("[INFO] Login button found — attempting automatic login...")
                page.click(LOGIN_BUTTON_SELECTOR)
                page.wait_for_timeout(2000)
                # Fill credentials if login form appears
                try:
                    page.fill("input[type='text'], input[type='email'], input[type='tel']", username)
                    page.fill("input[type='password']", password)
                    page.keyboard.press("Enter")
                    page.wait_for_timeout(4000)
                except Exception:
                    print("[WARN] Auto-login failed. Please log in manually in the browser.")
                    input("✅ After logging in, press Enter to continue...")
            else:
                print("[INFO] Not logged in. Please log in via the browser...")
                page.click(LOGIN_BUTTON_SELECTOR)
                page.wait_for_timeout(15000)
                input("✅ After logging in, press Enter to continue...")

        page.wait_for_selector(CHAPTER_SELECTOR)

        chapters = page.query_selector_all(CHAPTER_SELECTOR)
        print(f"[INFO] Found {len(chapters)} chapter(s).")

        chapters_data = []
        for ch_idx, ch in enumerate(chapters, start=1):
            ch_title_el = ch.query_selector(CHAPTER_TITLE_SELECTOR)
            ch_title = slugify(ch_title_el.inner_text()) if ch_title_el else f"Chapter_{ch_idx}"

            lessons = ch.query_selector_all(LESSON_SELECTOR)
            lesson_infos = []
            for l_idx, lesson in enumerate(lessons, start=1):
                l_title_el = lesson.query_selector(LESSON_TITLE_SELECTOR)
                l_title = (
                    slugify(l_title_el.get_attribute("title") or l_title_el.inner_text())
                    if l_title_el
                    else f"Lesson_{l_idx}"
                )
                lesson_href = lesson.get_attribute("href")
                if not lesson_href:
                    print(f"[WARN] Lesson {l_idx} in chapter {ch_idx} has no href, skipping.")
                    continue
                if not lesson_href.startswith("http"):
                    lesson_href = MAKTABKHOONEH_BASE + lesson_href
                lesson_infos.append((l_idx, l_title, lesson_href))

            chapters_data.append((ch_idx, ch_title, lesson_infos))

        for ch_idx, ch_title, lesson_infos in chapters_data:
            chapter_dir = output_dir / f"{ch_idx:02d} - {ch_title}"
            ensure_dir(chapter_dir)
            for l_idx, l_title, lesson_href in lesson_infos:
                out_path = chapter_dir / f"{l_idx:02d}-{l_title}.mp4"
                if skip_if_exists and out_path.exists():
                    print(f"[SKIP] {out_path.name}")
                    continue
                print(f"[INFO] Downloading: {out_path.name}")
                page.goto(lesson_href, wait_until="domcontentloaded")
                try:
                    page.wait_for_selector(DOWNLOAD_SELECTOR, timeout=15000)
                except Exception:
                    print(f"[ERROR] Download button not found for lesson {l_idx} (ch {ch_idx}), skipping.")
                    continue
                with page.expect_download(timeout=600_000) as dl_info:
                    page.click(DOWNLOAD_SELECTOR)
                dl_info.value.save_as(str(out_path))

        browser.close()


if __name__ == "__main__":
    main()
